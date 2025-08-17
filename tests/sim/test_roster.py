"""Tests for roster loading, distribution validation, and header error handling."""

from pathlib import Path

import pytest

from sharepoint_sim.roster import Roster

ROSTER_TOTAL = 100
INBOUND_COUNT = 40
OUTBOUND_COUNT = 40
HYBRID_COUNT = 20


def test_roster_loads_and_distribution() -> None:
    """Roster loads expected employee count, role distribution, and unique UUIDs."""
    roster = Roster()
    assert len(roster.employees) == ROSTER_TOTAL
    inbound = len(roster.by_role("inbound"))
    outbound = len(roster.by_role("outbound"))
    hybrid = len(roster.by_role("hybrid"))
    assert (inbound, outbound, hybrid) == (INBOUND_COUNT, OUTBOUND_COUNT, HYBRID_COUNT)
    assert len({e.uuid for e in roster.employees}) == ROSTER_TOTAL


def test_roster_header_validation(tmp_path: Path) -> None:
    """Invalid header raises ValueError with 'header mismatch' substring."""
    p = tmp_path / "bad.csv"
    p.write_text("id,name,role\n1,a,inbound\n")
    with pytest.raises(ValueError, match="header mismatch"):
        Roster(path=p)
