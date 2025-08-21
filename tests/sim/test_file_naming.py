from sharepoint_sim import __version__  # noqa: F401


def test_version_import_exists():
    assert isinstance(__version__, str)
