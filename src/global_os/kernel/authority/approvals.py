"""Signed approval tokens — bound to action_hash, optionally one-time."""

from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from global_os.common.hashing import content_hash, new_id


class ApprovalError(Exception):
    pass


class ApprovalInvalid(ApprovalError):
    pass


@dataclass(frozen=True)
class ApprovalToken:
    approval_id: str
    approver: str
    action_hash: str
    goal_id: str
    limits: dict[str, Any]
    valid_until: str
    one_time: bool
    signature: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "approver": self.approver,
            "action_hash": self.action_hash,
            "goal_id": self.goal_id,
            "limits": self.limits,
            "valid_until": self.valid_until,
            "one_time": self.one_time,
            "signature": self.signature,
        }


class ApprovalService:
    """HMAC-signed approvals. Secret never enters prompts/events (handle only)."""

    def __init__(self, conn: sqlite3.Connection, signing_key: bytes) -> None:
        self._conn = conn
        self._key = signing_key

    def issue(
        self,
        *,
        approver: str,
        action_hash: str,
        goal_id: str,
        limits: dict[str, Any],
        valid_until: str,
        one_time: bool = True,
    ) -> ApprovalToken:
        approval_id = new_id("apr")
        payload = {
            "approval_id": approval_id,
            "approver": approver,
            "action_hash": action_hash,
            "goal_id": goal_id,
            "limits": limits,
            "valid_until": valid_until,
            "one_time": one_time,
        }
        signature = self._sign(payload)
        self._conn.execute(
            """
            INSERT INTO approvals (
                approval_id, approver, action_hash, goal_id, limits_json,
                valid_until, one_time, consumed, signature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
            """,
            (
                approval_id,
                approver,
                action_hash,
                goal_id,
                json.dumps(limits),
                valid_until,
                1 if one_time else 0,
                signature,
            ),
        )
        self._conn.commit()
        return ApprovalToken(
            approval_id=approval_id,
            approver=approver,
            action_hash=action_hash,
            goal_id=goal_id,
            limits=limits,
            valid_until=valid_until,
            one_time=one_time,
            signature=signature,
        )

    def verify_and_consume(self, token: ApprovalToken, *, action_hash: str, goal_id: str) -> None:
        if token.action_hash != action_hash:
            raise ApprovalInvalid("approval action_hash mismatch")
        if token.goal_id != goal_id:
            raise ApprovalInvalid("approval goal_id mismatch")
        if datetime.fromisoformat(token.valid_until) < datetime.now(UTC):
            raise ApprovalInvalid("approval expired")
        expected = self._sign(
            {
                "approval_id": token.approval_id,
                "approver": token.approver,
                "action_hash": token.action_hash,
                "goal_id": token.goal_id,
                "limits": token.limits,
                "valid_until": token.valid_until,
                "one_time": token.one_time,
            }
        )
        if not hmac.compare_digest(expected, token.signature):
            raise ApprovalInvalid("invalid approval signature")
        row = self._conn.execute(
            "SELECT consumed, one_time FROM approvals WHERE approval_id = ?",
            (token.approval_id,),
        ).fetchone()
        if row is None:
            raise ApprovalInvalid("unknown approval")
        if row["one_time"] and row["consumed"]:
            raise ApprovalInvalid("one-time approval already consumed")
        if token.one_time:
            self._conn.execute(
                "UPDATE approvals SET consumed = 1 WHERE approval_id = ?",
                (token.approval_id,),
            )
            self._conn.commit()

    def _sign(self, payload: dict[str, Any]) -> str:
        digest = hmac.new(
            self._key,
            content_hash(payload).encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return f"hmac-sha256:{digest}"
