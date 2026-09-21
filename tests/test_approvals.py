from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from global_os.adapters.storage import connect_sqlite
from global_os.common.hashing import content_hash
from global_os.kernel.authority import ApprovalInvalid, ApprovalService


def test_approval_bound_to_action_hash_and_one_time():
    conn = connect_sqlite(":memory:")
    svc = ApprovalService(conn, signing_key=b"test-secret-key-32bytes-minimum!!")
    action_a = content_hash({"op": "buy_server"})
    action_b = content_hash({"op": "send_money"})
    until = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    token = svc.issue(
        approver="user_serge",
        action_hash=action_a,
        goal_id="goal_x",
        limits={"usd": 100},
        valid_until=until,
        one_time=True,
    )
    svc.verify_and_consume(token, action_hash=action_a, goal_id="goal_x")
    with pytest.raises(ApprovalInvalid, match="already consumed"):
        svc.verify_and_consume(token, action_hash=action_a, goal_id="goal_x")
    token2 = svc.issue(
        approver="user_serge",
        action_hash=action_a,
        goal_id="goal_x",
        limits={"usd": 100},
        valid_until=until,
        one_time=True,
    )
    with pytest.raises(ApprovalInvalid, match="action_hash"):
        svc.verify_and_consume(token2, action_hash=action_b, goal_id="goal_x")
