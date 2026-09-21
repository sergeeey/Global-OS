from __future__ import annotations

from pathlib import Path

from global_os.verification.source import SourceClaim, verify_source_claim


def test_source_claim_verification_on_constitution():
    root = Path(__file__).resolve().parents[1]
    ok = verify_source_claim(
        SourceClaim(
            statement="Intelligence is not authority",
            source_path="CONSTITUTION.md",
            required_substring="Intelligence ≠ Authority",
        ),
        root=root,
    )
    assert ok.passed is True
    bad = verify_source_claim(
        SourceClaim(
            statement="missing",
            source_path="CONSTITUTION.md",
            required_substring="THIS_STRING_DOES_NOT_EXIST_XYZ",
        ),
        root=root,
    )
    assert bad.passed is False
