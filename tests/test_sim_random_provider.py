"""Test RandomProvider edge cases for 100% coverage."""
from sharepoint_sim.random_provider import RandomProvider
from datetime import datetime, UTC

def test_random_provider_now_uses_clock():
    called = {}
    def fake_clock():
        called["yes"] = True
        return datetime(2025, 8, 17, 12, 0, tzinfo=UTC)
    rp = RandomProvider(seed=123, clock=fake_clock)
    assert rp.now() == datetime(2025, 8, 17, 12, 0, tzinfo=UTC)
    assert called["yes"]
