"""Cross-generator header + role rule tests and determinism checks."""

from sharepoint_sim.datasets.acq import ACQGenerator
from sharepoint_sim.datasets.campaign_interactions import CampaignInteractionsGenerator
from sharepoint_sim.datasets.dials import DialsGenerator
from sharepoint_sim.datasets.ib_calls import IBCallsGenerator
from sharepoint_sim.datasets.productivity import ProductivityGenerator
from sharepoint_sim.datasets.qcbs import QCBSGenerator
from sharepoint_sim.datasets.resc import RESCGenerator
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster
from sharepoint_sim.schemas import (
    ACQ_HEADERS,
    CAMPAIGN_INTERACTIONS_HEADERS,
    DIALS_HEADERS,
    IB_CALLS_HEADERS,
    PRODUCTIVITY_HEADERS,
    QCBS_HEADERS,
    RESC_HEADERS,
    ROLE_RULES,
)

ROWS_HEADER_SAMPLE = 20
ROWS_DETERMINISM = 15


def build(seed: int = 123) -> tuple[Roster, RandomProvider]:  # pragma: no cover - helper
    """Build roster + random provider with provided seed."""
    roster = Roster()
    rnd = RandomProvider(seed=seed)
    return roster, rnd


def test_headers_match_and_roles_enforced() -> None:
    """Each generator's headers set matches schema and roles restricted appropriately."""
    roster, rnd = build()
    gens = [
        (ACQGenerator(roster, rnd), ACQ_HEADERS),
        (ProductivityGenerator(roster, rnd), PRODUCTIVITY_HEADERS),
        (QCBSGenerator(roster, rnd), QCBS_HEADERS),
        (RESCGenerator(roster, rnd), RESC_HEADERS),
        (DialsGenerator(roster, rnd), DIALS_HEADERS),
        (IBCallsGenerator(roster, rnd), IB_CALLS_HEADERS),
        (CampaignInteractionsGenerator(roster, rnd), CAMPAIGN_INTERACTIONS_HEADERS),
    ]
    for gen, headers in gens:
        rows = gen.build(ROWS_HEADER_SAMPLE)
        assert set(rows[0].keys()) == set(headers)
        allowed = ROLE_RULES[gen.name]
        # Campaign_Interactions may not have Agent Id for every row.
        if gen.name != "Campaign_Interactions":
            valid_ids = {e.uuid for e in roster.employees if e.role in allowed}
            assert all(r.get("Agent Id") in valid_ids for r in rows if "Agent Id" in r)


def test_determinism_same_seed_all_generators() -> None:
    """Same seed produces identical rows across fresh generator instances."""
    roster, rnd1 = build(999)
    _, rnd2 = build(999)
    gens1 = [
        ACQGenerator(roster, rnd1),
        ProductivityGenerator(roster, rnd1),
        QCBSGenerator(roster, rnd1),
        RESCGenerator(roster, rnd1),
        DialsGenerator(roster, rnd1),
        IBCallsGenerator(roster, rnd1),
        CampaignInteractionsGenerator(roster, rnd1),
    ]
    gens2 = [
        ACQGenerator(roster, rnd2),
        ProductivityGenerator(roster, rnd2),
        QCBSGenerator(roster, rnd2),
        RESCGenerator(roster, rnd2),
        DialsGenerator(roster, rnd2),
        IBCallsGenerator(roster, rnd2),
        CampaignInteractionsGenerator(roster, rnd2),
    ]
    for g1, g2 in zip(gens1, gens2, strict=False):
        r1 = g1.build(ROWS_DETERMINISM)
        r2 = g2.build(ROWS_DETERMINISM)
        assert r1 == r2
