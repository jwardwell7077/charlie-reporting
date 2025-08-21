"""Test Roster error branches for 100% coverage."""
import pytest
from sharepoint_sim.roster import Roster
from pathlib import Path

def test_roster_size_error(tmp_path: Path) -> None:
    # Write a CSV with only 2 employees
    csv_path = tmp_path / "roster.csv"
    csv_path.write_text("uuid,name,role\n1,A,inbound\n2,B,hybrid\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Roster must contain exactly 100 employees"):
        Roster.from_csv(csv_path)

def test_roster_unknown_role(tmp_path: Path) -> None:
    # Write a CSV with an unknown role
    csv_path = tmp_path / "roster.csv"
    csv_path.write_text("uuid,name,role\n1,A,foo\n" + "".join(f"{i},B,inbound\n" for i in range(2,101)), encoding="utf-8")
    with pytest.raises(ValueError, match="Unexpected role: foo"):
        Roster.from_csv(csv_path)

def test_roster_header_mismatch(tmp_path: Path) -> None:
    # Write a CSV with wrong headers
    csv_path = tmp_path / "roster.csv"
    csv_path.write_text("id,fullname,position\n1,A,inbound\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Roster header mismatch"):
        Roster.from_csv(csv_path)
