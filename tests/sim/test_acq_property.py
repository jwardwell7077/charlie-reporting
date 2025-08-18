"""Property-based tests for ACQGenerator invariants using Hypothesis."""
from hypothesis import given, strategies as st
from sharepoint_sim.datasets.acq import ACQGenerator, ACQ_HEADERS
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster
from sharepoint_sim.schemas import ROLE_RULES

@given(
    row_count=st.integers(min_value=1, max_value=2000),
    seed=st.integers(min_value=0, max_value=2**32 - 1),
)
def test_acq_generator_invariants(row_count: int, seed: int) -> None:
    """ACQGenerator: headers, role, and handle invariants hold for any row count and seed."""
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    gen = ACQGenerator(roster, rnd)
    count = gen.row_count(row_count)
    rows = gen.build(count)
    # All rows have correct headers
    assert all(list(r.keys()) == ACQ_HEADERS for r in rows)
    # All Agent roles are allowed
    allowed = ROLE_RULES[gen.name]
    uuid_to_role = {e.uuid: e.role for e in roster.employees}
    for r in rows:
        assert uuid_to_role[r["Agent Id"]] in allowed
        # Handle is integer string in [0, 25]
        handle = int(r["Handle"])
        assert 0 <= handle <= 25
    # Row count matches requested clamp
    assert count == max(10, min(1000, row_count))
