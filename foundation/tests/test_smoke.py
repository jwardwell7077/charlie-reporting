"""Basic structural smoke tests for the `Settings` model."""

from config.settings import Settings


def test_settings_model_slots() -> None:
    """`Settings` dataclass exposes expected slot-backed field names."""
    fields = {f.name for f in Settings.__dataclass_fields__.values()}
    expected = {"schedules", "data_sources", "collector", "report", "email"}
    assert expected.issubset(fields)

    # Ensure __slots__ present (dataclass with slots=True) and contains at least the expected fields
    assert hasattr(Settings, "__slots__")
    slots = set(getattr(Settings, "__slots__"))
    assert expected.issubset(slots)
