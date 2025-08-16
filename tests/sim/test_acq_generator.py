from sharepoint_sim.roster import load_roster
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.datasets.acq import ACQGenerator, ACQ_HEADERS


def test_acq_row_count_bounds():
    roster = load_roster()
    rnd = RandomProvider(seed=123)
    gen = ACQGenerator(roster, rnd)
    assert gen.row_count(None) == 50
    assert gen.row_count(5) == 10
    assert gen.row_count(2000) == 1000


def test_acq_generation_deterministic():
    roster = load_roster()
    rnd1 = RandomProvider(seed=999)
    rnd2 = RandomProvider(seed=999)
    g1 = ACQGenerator(roster, rnd1)
    g2 = ACQGenerator(roster, rnd2)
    rows1 = g1.build(15)
    rows2 = g2.build(15)
    assert rows1 == rows2
    assert all(r.keys() == set(ACQ_HEADERS) for r in rows1)
