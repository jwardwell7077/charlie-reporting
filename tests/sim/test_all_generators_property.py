"""Property-based tests for all SharePoint dataset generators using Hypothesis."""
from hypothesis import given, strategies as st
from sharepoint_sim.datasets.acq import ACQGenerator, ACQ_HEADERS
from sharepoint_sim.datasets.productivity import ProductivityGenerator, PRODUCTIVITY_HEADERS
from sharepoint_sim.datasets.qcbs import QCBSGenerator, QCBS_HEADERS
from sharepoint_sim.datasets.resc import RESCGenerator, RESC_HEADERS
from sharepoint_sim.datasets.ib_calls import IBCallsGenerator, IB_CALLS_HEADERS
from sharepoint_sim.datasets.dials import DialsGenerator, DIALS_HEADERS
from sharepoint_sim.datasets.campaign_interactions import CampaignInteractionsGenerator, CAMPAIGN_INTERACTIONS_HEADERS
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster
from sharepoint_sim.schemas import ROLE_RULES

# Helper for all generators
row_count_strategy = st.integers(min_value=1, max_value=2000)
seed_strategy = st.integers(min_value=0, max_value=2**32 - 1)

@given(row_count=row_count_strategy, seed=seed_strategy)
def test_productivity_generator_invariants(row_count: int, seed: int) -> None:
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    gen = ProductivityGenerator(roster, rnd)
    count = gen.row_count(row_count)
    rows = gen.build(count)
    allowed = ROLE_RULES[gen.name]
    uuid_to_role = {e.uuid: e.role for e in roster.employees}
    for r in rows:
        assert list(r.keys()) == PRODUCTIVITY_HEADERS
        assert uuid_to_role[r["Agent Id"]] in allowed
        logged_in = int(r["Logged In"])
        buckets = [int(r["On Queue"]), int(r["Idle"]), int(r["Off Queue"]), int(r["Interacting"])]
        assert sum(buckets) <= logged_in
        assert 200 <= logged_in <= 480
    assert count == max(10, min(1000, row_count))

@given(row_count=row_count_strategy, seed=seed_strategy)
def test_qcbs_generator_invariants(row_count: int, seed: int) -> None:
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    gen = QCBSGenerator(roster, rnd)
    count = gen.row_count(row_count)
    rows = gen.build(count)
    allowed = ROLE_RULES[gen.name]
    uuid_to_role = {e.uuid: e.role for e in roster.employees}
    for r in rows:
        assert list(r.keys()) == QCBS_HEADERS
        assert uuid_to_role[r["Agent Id"]] in allowed
        handle = int(r["Handle"])
        assert 0 <= handle <= 25
    assert count == max(10, min(1000, row_count))

@given(row_count=row_count_strategy, seed=seed_strategy)
def test_resc_generator_invariants(row_count: int, seed: int) -> None:
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    gen = RESCGenerator(roster, rnd)
    count = gen.row_count(row_count)
    rows = gen.build(count)
    allowed = ROLE_RULES[gen.name]
    uuid_to_role = {e.uuid: e.role for e in roster.employees}
    for r in rows:
        assert list(r.keys()) == RESC_HEADERS
        assert uuid_to_role[r["Agent Id"]] in allowed
        handle = int(r["Handle"])
        assert 0 <= handle <= 25
    assert count == max(10, min(1000, row_count))

@given(row_count=row_count_strategy, seed=seed_strategy)
def test_ib_calls_generator_invariants(row_count: int, seed: int) -> None:
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    gen = IBCallsGenerator(roster, rnd)
    count = gen.row_count(row_count)
    rows = gen.build(count)
    allowed = ROLE_RULES[gen.name]
    uuid_to_role = {e.uuid: e.role for e in roster.employees}
    for r in rows:
        assert list(r.keys()) == IB_CALLS_HEADERS
        assert uuid_to_role[r["Agent Id"]] in allowed
        handle = int(r["Handle"])
        avg_handle = int(r["Avg Handle"])
        assert 0 <= handle <= 25
        assert handle == avg_handle
    assert count == max(10, min(1000, row_count))

@given(row_count=row_count_strategy, seed=seed_strategy)
def test_dials_generator_invariants(row_count: int, seed: int) -> None:
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    gen = DialsGenerator(roster, rnd)
    count = gen.row_count(row_count)
    rows = gen.build(count)
    allowed = ROLE_RULES[gen.name]
    uuid_to_role = {e.uuid: e.role for e in roster.employees}
    for r in rows:
        assert list(r.keys()) == DIALS_HEADERS
        assert uuid_to_role[r["Agent Id"]] in allowed
        handle = int(r["Handle"])
        avg_handle = int(r["Avg Handle"])
        avg_talk = int(r["Avg Talk"])
        avg_hold = int(r["Avg Hold"])
        avg_acw = int(r["Avg ACW"])
        assert 0 <= handle <= 25
        assert avg_handle == handle
        assert 0 <= avg_talk <= handle
        assert 0 <= avg_hold <= (handle - avg_talk)
        assert 0 <= avg_acw <= 10
        # Totals
        assert int(r["Total Handle"]) == handle * 5
        assert int(r["Total Talk"]) == avg_talk * 5
        assert int(r["Total Hold"]) == avg_hold * 5
        assert int(r["Total ACW"]) == avg_acw * 5
    assert count == max(10, min(1000, row_count))

@given(row_count=row_count_strategy, seed=seed_strategy)
def test_campaign_interactions_generator_invariants(row_count: int, seed: int) -> None:
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    gen = CampaignInteractionsGenerator(roster, rnd)
    count = gen.row_count(row_count)
    rows = gen.build(count)
    for r in rows:
        assert list(r.keys()) == CAMPAIGN_INTERACTIONS_HEADERS
        assert r["Users"] in {e.uuid for e in roster.employees}
        assert r["Initial Direction"] in {"inbound", "outbound"}
    assert count == max(10, min(1000, row_count))
