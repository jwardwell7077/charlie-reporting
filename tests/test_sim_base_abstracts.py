"""Tests for DatasetGenerator abstract base class error branches (100% coverage)."""
import pytest
from sharepoint_sim.datasets.base import DatasetGenerator
from sharepoint_sim.roster import Roster
from sharepoint_sim.random_provider import RandomProvider


class DummyGen(DatasetGenerator):
    name = "DUMMY"
    headers = ("A",)
    def row_count(self, requested=None):
        return super().row_count(requested)
    def generate_rows(self, count):
        return super().generate_rows(count)


def test_row_count_not_implemented():
    gen = DummyGen(Roster(), RandomProvider(seed=42))
    with pytest.raises(NotImplementedError):
        gen.row_count()

def test_generate_rows_not_implemented():
    gen = DummyGen(Roster(), RandomProvider(seed=42))
    with pytest.raises(NotImplementedError):
        gen.generate_rows(1)
