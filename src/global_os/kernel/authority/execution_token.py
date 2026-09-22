"""Proposal-bound ExecutionToken — Gateway verifies binding; ledger stores hash only.

GOS-I02/I03: token binds proposal_hash, principal, capability, resource, goal/version,
expiry, and one-time jti. Raw bearer never enters the Event Ledger.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from global_os.common.hashing import content_hash, new_id


class ExecutionTokenError(Exception):
    pass


class ExecutionTokenInvalid(ExecutionTokenError):
    pass


class ExecutionTokenExpired(ExecutionTokenInvalid):
    pass


class ExecutionTokenReplay(ExecutionTokenInvalid):
    pass


class ExecutionTokenBindingMismatch(ExecutionTokenInvalid):
    pass


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    pad = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)


@dataclass(frozen=True)
class ExecutionTokenClaims:
    jti: str
    token_id: str
    proposal_hash: str
    principal_id: str
    capability: str
    resource: str
    goal_id: str
    goal_version: int | str | None
    expires_at: str  # ISO8601 UTC

    def to_dict(self) -> dict[str, Any]:
        return {
            "jti": self.jti,
            "token_id": self.token_id,
            "proposal_hash": self.proposal_hash,
            "principal_id": self.principal_id,
            "capability": self.capability,
            "resource": self.resource,
            "goal_id": self.goal_id,
            "goal_version": self.goal_version,
            "expires_at": self.expires_at,
        }


@dataclass(frozen=True)
class MintedExecutionToken:
    claims: ExecutionTokenClaims
    bearer: str

    @property
    def token_id(self) -> str:
        return self.claims.token_id

    @property
    def token_hash(self) -> str:
        return content_hash({"token_id": self.token_id, "jti": self.claims.jti})


class ExecutionTokenService:
    """HMAC-signed proposal-bound tokens. Secret never enters prompts/events."""

    def __init__(self, signing_key: bytes | None = None, *, default_ttl_s: int = 120) -> None:
        key = signing_key
        if key is None:
            env = os.environ.get("GOS_EXECUTION_TOKEN_SECRET")
            key = env.encode("utf-8") if env else b"gos-dev-execution-token-key-not-for-prod"
        self._key = key
        self._default_ttl_s = default_ttl_s
        self._consumed_jti: set[str] = set()

    def mint(
        self,
        *,
        proposal: dict[str, Any],
        proposal_hash: str,
        ttl_s: int | None = None,
    ) -> MintedExecutionToken:
        ttl = self._default_ttl_s if ttl_s is None else ttl_s
        expires = datetime.now(UTC) + timedelta(seconds=ttl)
        claims = ExecutionTokenClaims(
            jti=new_id("jti"),
            token_id=new_id("et"),
            proposal_hash=proposal_hash,
            principal_id=str(proposal["principal_id"]),
            capability=str(proposal["capability"]),
            resource=str(proposal.get("resource", "")),
            goal_id=str(proposal["goal_id"]),
            goal_version=proposal.get("goal_version"),
            expires_at=expires.isoformat(),
        )
        body = _b64url(json.dumps(claims.to_dict(), sort_keys=True, separators=(",", ":")).encode())
        sig = self._sign(body)
        bearer = f"et1.{body}.{sig}"
        return MintedExecutionToken(claims=claims, bearer=bearer)

    def verify_binding(
        self,
        bearer: str,
        *,
        proposal: dict[str, Any],
        proposal_hash: str | None = None,
        now: datetime | None = None,
    ) -> ExecutionTokenClaims:
        claims = self.parse_and_verify_signature(bearer)
        clock = now or datetime.now(UTC)
        exp = datetime.fromisoformat(claims.expires_at)
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=UTC)
        if exp < clock:
            raise ExecutionTokenExpired("execution token expired")
        if claims.jti in self._consumed_jti:
            raise ExecutionTokenReplay("execution token jti already consumed")

        expected_hash = proposal_hash or content_hash(proposal)
        checks = [
            (claims.proposal_hash, expected_hash, "proposal_hash"),
            (claims.principal_id, str(proposal.get("principal_id")), "principal_id"),
            (claims.capability, str(proposal.get("capability")), "capability"),
            (claims.resource, str(proposal.get("resource", "")), "resource"),
            (claims.goal_id, str(proposal.get("goal_id")), "goal_id"),
        ]
        for got, want, label in checks:
            if got != want:
                raise ExecutionTokenBindingMismatch(f"execution token {label} mismatch")
        if (
            claims.goal_version is not None
            and proposal.get("goal_version") is not None
            and claims.goal_version != proposal.get("goal_version")
        ):
            raise ExecutionTokenBindingMismatch("execution token goal_version mismatch")
        return claims

    def consume(self, claims: ExecutionTokenClaims) -> None:
        if claims.jti in self._consumed_jti:
            raise ExecutionTokenReplay("execution token jti already consumed")
        self._consumed_jti.add(claims.jti)

    def verify_and_consume(
        self,
        bearer: str,
        *,
        proposal: dict[str, Any],
        proposal_hash: str | None = None,
    ) -> ExecutionTokenClaims:
        claims = self.verify_binding(bearer, proposal=proposal, proposal_hash=proposal_hash)
        self.consume(claims)
        return claims

    def parse_and_verify_signature(self, bearer: str) -> ExecutionTokenClaims:
        parts = bearer.split(".")
        if len(parts) != 3 or parts[0] != "et1":
            raise ExecutionTokenInvalid("malformed execution token")
        _hdr, body, sig = parts
        expected = self._sign(body)
        if not hmac.compare_digest(expected, sig):
            raise ExecutionTokenInvalid("invalid execution token signature")
        try:
            raw = json.loads(_b64url_decode(body).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ExecutionTokenInvalid("invalid execution token body") from exc
        required = {
            "jti",
            "token_id",
            "proposal_hash",
            "principal_id",
            "capability",
            "resource",
            "goal_id",
            "expires_at",
        }
        if not required.issubset(raw):
            raise ExecutionTokenInvalid("execution token missing claims")
        return ExecutionTokenClaims(
            jti=str(raw["jti"]),
            token_id=str(raw["token_id"]),
            proposal_hash=str(raw["proposal_hash"]),
            principal_id=str(raw["principal_id"]),
            capability=str(raw["capability"]),
            resource=str(raw["resource"]),
            goal_id=str(raw["goal_id"]),
            goal_version=raw.get("goal_version"),
            expires_at=str(raw["expires_at"]),
        )

    def ledger_refs(self, minted: MintedExecutionToken) -> dict[str, str]:
        """Safe refs for Event Ledger — never the raw bearer."""
        return {
            "execution_token_id": minted.token_id,
            "execution_token_hash": minted.token_hash,
            "execution_token_jti_hash": content_hash(minted.claims.jti),
        }

    def _sign(self, body: str) -> str:
        digest = hmac.new(self._key, body.encode("utf-8"), hashlib.sha256).hexdigest()
        return digest
