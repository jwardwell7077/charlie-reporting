"""Tests for ACQ dataset generator: row count bounds and determinism."""

from sharepoint_sim.datasets.acq import ACQ_HEADERS, ACQGenerator
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster

DEFAULT = 50
MIN_ROWS = 10
MAX_ROWS = 1000


def test_acq_row_count_bounds() -> None:
    """Row count clamps to [MIN_ROWS, MAX_ROWS] and defaults to DEFAULT when None."""
    roster = Roster()
    rnd = RandomProvider(seed=123)
    gen = ACQGenerator(roster, rnd)
    assert gen.row_count(None) == DEFAULT
    assert gen.row_count(5) == MIN_ROWS
    assert gen.row_count(2000) == MAX_ROWS


def test_acq_generation_deterministic() -> None:
    """Same seed yields identical output rows including column order."""
    roster = Roster()
    rnd1 = RandomProvider(seed=999)
    rnd2 = RandomProvider(seed=999)
    g1 = ACQGenerator(roster, rnd1)
    g2 = ACQGenerator(roster, rnd2)
    rows1 = g1.build(15)
    rows2 = g2.build(15)
    assert rows1 == rows2
    assert all(list(r.keys()) == ACQ_HEADERS for r in rows1)
