"""Smoke test ensuring package exposes __version__ string."""

from sharepoint_sim import __version__  # noqa: F401


def test_version_import_exists() -> None:
    """__version__ attribute is a string."""
    assert isinstance(__version__, str)
