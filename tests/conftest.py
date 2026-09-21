from __future__ import annotations

from datetime import UTC, datetime

import pytest


@pytest.fixture
def sample_goal():
    def _factory(**overrides):
        base = {
            "schema_version": "0.1.0",
            "goal_id": "goal_repo_audit_001",
            "version": 1,
            "tenant_id": "tenant_local",
            "workspace_id": "ws_dev",
            "objective": {"text": "Audit the repository without modifying it."},
            "success_criteria": [
                {"id": "sc_01", "description": "verified engineering report produced"}
            ],
            "invariants": ["read_only_target_repo"],
            "non_goals": ["modify_production"],
            "forbidden_outcomes": ["push_to_remote"],
            "risk": {"tolerance": "low", "maximum_irreversibility": "none"},
            "authority": {
                "delegation_depth_max": 3,
                "capabilities": ["filesystem.read", "web.read", "code.execute.sandbox"],
            },
            "evidence_requirements": {"major_finding": {"verification_tier": 2}},
            "termination": ["success_criteria_met", "user_cancelled"],
            "created_at": datetime.now(UTC).isoformat(),
        }
        base.update(overrides)
        return base

    return _factory


@pytest.fixture
def sample_proposal():
    def _factory(**overrides):
        base = {
            "proposal_id": "ap_canary_001",
            "schema_version": "0.1.0",
            "principal_id": "worker_research_1",
            "goal_id": "goal_repo_audit_001",
            "capability": "web.read",
            "resource": "https://example.com",
            "intended_effect": "page_fetched",
            "maximum_effect": "page_fetched",
            "reversible": True,
            "information_disclosure": "none",
            "monetary_cost": 0,
            "idempotency_key": "idem-canary-001",
            "evidence_refs": [],
            "approval_refs": [],
            "context": {},
            "parent_capabilities": ["web.read", "filesystem.read"],
        }
        base.update(overrides)
        return base

    return _factory
