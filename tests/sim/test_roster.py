from pathlib import Path

from sharepoint_sim.roster import load_roster


def test_roster_loads_and_distribution():
    roster = load_roster()
    assert len(roster.employees) == 100
    inbound = len(roster.by_role("inbound"))
    outbound = len(roster.by_role("outbound"))
    hybrid = len(roster.by_role("hybrid"))
    # Expect 40 inbound, 40 outbound, 20 hybrid
    assert (inbound, outbound, hybrid) == (40, 40, 20)
    # All uuids unique
    assert len({e.uuid for e in roster.employees}) == 100


def test_roster_header_validation(tmp_path: Path):
    p = tmp_path / "bad.csv"
    p.write_text("id,name,role\n1,a,inbound\n")
    try:
        load_roster(p)  # should raise
    except ValueError as e:
        assert "header mismatch" in str(e)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected ValueError for bad header")
