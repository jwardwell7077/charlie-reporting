"""Dataset generator header & role constraint tests (initial subset)."""
from __future__ import annotations

from sharepoint_sim.roster import load_roster
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.datasets.acq import ACQGenerator, ACQ_HEADERS

EXPECTED = {
    "ACQ": ACQ_HEADERS,
}

ROLE_RULES = {
    "ACQ": {"inbound", "hybrid"},
}


def build(generator_cls):  # type: ignore[no-untyped-def]
    roster = load_roster()
    rnd = RandomProvider(seed=42)
    gen = generator_cls(roster, rnd)
    rows = gen.build(15)
    return gen, rows


def test_acq_headers_and_roles():
    gen, rows = build(ACQGenerator)
    assert list(gen.headers) == EXPECTED[gen.name]
    allowed = ROLE_RULES[gen.name]
    uuids = {r["Agent Id"] for r in rows}
    roster = load_roster()
    role_map = {e.uuid: e.role for e in roster.employees}
    assert {role_map[u] for u in uuids}.issubset(allowed)
