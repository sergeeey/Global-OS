"""P2/P3: grounding, SOP packs, research factory templates (ADR-0013)."""

from __future__ import annotations

from pathlib import Path

from global_os.cognition.missions.research_factory import (
    RESEARCH_FACTORY_STAGES,
    ResearchFactoryRunner,
    StageId,
    mission_contract_template,
)
from global_os.cognition.skills.sop_pack import (
    hierarchy_not_default_axiom,
    load_sop_pack,
    validate_handoff,
)
from global_os.verification.grounding import ground_claim, may_promote_claim


def test_citation_less_claim_rejected(tmp_path: Path) -> None:
    r = ground_claim(statement="X is true", citations=[], root=tmp_path)
    assert r.grounded is False
    assert may_promote_claim(r) is False


def test_grounded_claim_with_passage(tmp_path: Path) -> None:
    src = tmp_path / "paper.md"
    src.write_text("We observe that water boils at 100C.\n", encoding="utf-8")
    r = ground_claim(
        statement="water boils at 100C",
        citations=[{"source_path": "paper.md", "passage": "boils at 100C"}],
        root=tmp_path,
    )
    assert r.grounded is True
    assert may_promote_claim(r) is True


def test_sop_pack_typed_handoff_and_no_hierarchy_axiom() -> None:
    pack = load_sop_pack("sop.software.v1")
    assert hierarchy_not_default_axiom(pack)
    missing = validate_handoff(pack, "prd", {"user_stories": ["a"]})
    assert "acceptance_criteria" in missing
    ok = validate_handoff(
        pack, "prd", {"user_stories": ["a"], "acceptance_criteria": ["b"]}
    )
    assert ok == []


def test_research_factory_reject_allowed_and_self_cert_denied() -> None:
    tpl = mission_contract_template(goal_id="g1", title="demo")
    assert "llm_peer_review_as_verified" in tpl["forbidden"]
    runner = ResearchFactoryRunner()
    for stage in RESEARCH_FACTORY_STAGES:
        runner.run_stage(
            stage,
            prereg_locked=True,
            mechanical_ok=True,
            independent_diversity=True,
            advisory_llm_review="looks fine",
        )
    assert runner.terminal()["terminal"] == "COMPLETED"

    runner2 = ResearchFactoryRunner()
    runner2.run_stage(
        StageId.RUN,
        prereg_locked=False,
        mechanical_ok=True,
        independent_diversity=True,
    )
    assert runner2.terminal()["terminal"] == "REJECTED"
    assert ResearchFactoryRunner.self_cert_path_denied() is True
