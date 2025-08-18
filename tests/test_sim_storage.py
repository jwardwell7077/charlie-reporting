"""Test Storage and StoredFile for 100% coverage."""
from sharepoint_sim.storage import Storage, StoredFile
from pathlib import Path
import os

def test_storage_write_list_reset(tmp_path):
    s = Storage(tmp_path)
    # Write a file
    fpath = s.write_csv("foo.csv", ["A", "B"], [{"A": "1", "B": "2"}])
    assert fpath.exists()
    files = s.list_files()
    assert files and files[0].name == "foo.csv"
    assert files[0].size() == os.path.getsize(fpath)
    s.reset()
    assert not s.list_files()
