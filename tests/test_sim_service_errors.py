"""Test SharePointCSVGenerator error/edge cases for 100% coverage."""
import pytest
from sharepoint_sim.service import SharePointCSVGenerator
from pathlib import Path

def test_get_generator_unknown_dataset():
    svc = SharePointCSVGenerator(root_dir=Path("/tmp"), seed=42)
    with pytest.raises(ValueError, match="Unknown dataset"):  # covers error branch
        svc._get_generator("DOES_NOT_EXIST")

def test_generate_many_with_dict_rows():
    svc = SharePointCSVGenerator(root_dir=Path("/tmp"), seed=42)
    # Should not raise, just cover the dict/int logic
    svc.generate_many(["ACQ", "Productivity"], rows={"ACQ": 10, "Productivity": 12})
    svc.generate_many(["ACQ", "Productivity"], rows=15)
    svc.generate_many(["ACQ", "Productivity"], rows=None)

def test_reset_clears_roster_and_files(tmp_path):
    svc = SharePointCSVGenerator(root_dir=tmp_path, seed=42)
    # Generate a file
    svc.generate("ACQ", 10)
    assert svc.list_files()
    svc.reset()
    assert not svc.list_files()
    # Roster should be reloaded after reset
    svc.generate("ACQ", 10)
    assert svc.list_files()
