"""Tests for dataset generator headers and role constraints.

Focuses on verifying that ACQ dataset headers match the schema constant and
that generated rows only use allowed employee roles.
"""
from __future__ import annotations

from sharepoint_sim.datasets.acq import ACQ_HEADERS, ACQGenerator
from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.random_provider import RandomProvider
from sharepoint_sim.roster import Roster
from sharepoint_sim.schemas import ROLE_RULES

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SEED = 42
ROW_REQUEST = 15
DATASET = "ACQ"
ALLOWED_ROLES = ROLE_RULES[DATASET]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build(
    generator_cls: type[DatasetGenerator],
) -> tuple[DatasetGenerator, list[dict[str, str]]]:
    """Instantiate a generator, build rows, and return both.

    Args:
        generator_cls (Type[DatasetGenerator]): Concrete generator class.

    Returns:
        tuple[DatasetGenerator, list[dict[str, str]]]: The instantiated generator and generated rows.
    """
    roster = Roster()
    rnd = RandomProvider(seed=SEED)
    gen = generator_cls(roster, rnd)
    rows = gen.build(ROW_REQUEST)
    return gen, rows

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_acq_headers_and_roles() -> None:
    """ACQ headers match spec and roles used are within allowed set."""
    gen, rows = build(ACQGenerator)
    assert list(gen.headers) == ACQ_HEADERS
    uuids = {r["Agent Id"] for r in rows}
    role_map = {e.uuid: e.role for e in Roster().employees}
    used_roles = {role_map[u] for u in uuids}
    assert used_roles.issubset(
        ALLOWED_ROLES
    ), f"Unexpected roles: {used_roles - ALLOWED_ROLES}"
