"""Targeted regression test for ProductivityGenerator bucket allocation edge case."""
from sharepoint_sim.datasets.productivity import ProductivityGenerator
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster

def test_productivity_generator_no_bucket_overflow():
    """Sum of activity buckets never exceeds Logged In, even for edge seeds and low logged_in."""
    # Use a seed and row count that previously triggered the bug
    roster = Roster()
    rnd = RandomProvider(seed=0)
    gen = ProductivityGenerator(roster, rnd)
    rows = gen.build(1)
    for r in rows:
        logged_in = int(r["Logged In"])
        buckets = [int(r["On Queue"]), int(r["Idle"]), int(r["Off Queue"]), int(r["Interacting"])]
        assert sum(buckets) <= logged_in, f"Buckets sum {sum(buckets)} > Logged In {logged_in} (row: {r})"
