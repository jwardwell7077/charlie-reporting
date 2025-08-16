from sharepoint_sim.roster import load_roster
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.schemas import (
    ACQ_HEADERS, PRODUCTIVITY_HEADERS, QCBS_HEADERS, RESC_HEADERS,
    DIALS_HEADERS, IB_CALLS_HEADERS, CAMPAIGN_INTERACTIONS_HEADERS, ROLE_RULES
)
from sharepoint_sim.datasets.acq import ACQGenerator
from sharepoint_sim.datasets.productivity import ProductivityGenerator
from sharepoint_sim.datasets.qcbs import QCBSGenerator
from sharepoint_sim.datasets.resc import RESCGenerator
from sharepoint_sim.datasets.dials import DialsGenerator
from sharepoint_sim.datasets.ib_calls import IBCallsGenerator
from sharepoint_sim.datasets.campaign_interactions import CampaignInteractionsGenerator


def build(seed: int = 123):
    roster = load_roster()
    rnd = RandomProvider(seed=seed)
    return roster, rnd


def test_headers_match_and_roles_enforced():
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
        rows = gen.build(20)
        assert set(rows[0].keys()) == set(headers)
        allowed = ROLE_RULES[gen.name]
        assert all(r["Agent Id"] in {e.uuid for e in roster.employees if e.role in allowed} or gen.name == "Campaign_Interactions" for r in rows if "Agent Id" in r)


def test_determinism_same_seed_all_generators():
    roster, rnd1 = build(999)
    _, rnd2 = build(999)
    gens1 = [ACQGenerator(roster, rnd1), ProductivityGenerator(roster, rnd1), QCBSGenerator(roster, rnd1), RESCGenerator(roster, rnd1), DialsGenerator(roster, rnd1), IBCallsGenerator(roster, rnd1), CampaignInteractionsGenerator(roster, rnd1)]
    gens2 = [ACQGenerator(roster, rnd2), ProductivityGenerator(roster, rnd2), QCBSGenerator(roster, rnd2), RESCGenerator(roster, rnd2), DialsGenerator(roster, rnd2), IBCallsGenerator(roster, rnd2), CampaignInteractionsGenerator(roster, rnd2)]
    for g1, g2 in zip(gens1, gens2):
        r1 = g1.build(15)
        r2 = g2.build(15)
        assert r1 == r2
