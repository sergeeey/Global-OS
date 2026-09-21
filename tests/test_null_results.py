from __future__ import annotations

from global_os.memory import NullResultStore
from global_os.runtime.events import EventLedger


def test_null_result_persists_and_warns_on_repeat():
    ledger = EventLedger()
    store = NullResultStore(ledger)
    store.record(
        attempt="scrape_js_heavy_site",
        why_failed="blocked by captcha",
        evidence=["ev_x"],
        conditions="site X",
        reopen_condition="captcha solver approved",
        tenant_id="t",
        workspace_id="w",
        goal_id="goal_x",
    )
    assert len(store.list_all()) == 1
    warn = store.warn_if_repeat("scrape_js_heavy_site")
    assert warn is not None
    assert "reopen_condition" in warn
    types = [e["event_type"] for e in ledger.list_events()]
    assert "null_result.recorded" in types
