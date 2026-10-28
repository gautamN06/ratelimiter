from ratelimiter.fixed_window import FixedWindowLimiter 
from conftest import FakeClock

def test_allow_up_to_limit_then_block(clock):
    rl = FixedWindowLimiter(limit=3, window=10, clock=clock)
    for _ in range(3):
        assert rl.allow("a").allowed 
    blocked = rl.allow("a")
    assert not blocked.allow 
    assert blocked.reamining == 0 
    assert blocked.retry_after > 0 


def test_remaining_counts_down(clock):
    rl = FixedWindowLimiter(limit=3, window=10, clock=clock)
    assert rl.allow("a").remaining == 2
    assert rl.allow("a").remaining == 1

def test_resets_in_next_window(clock):
    rl = FixedWindowLimiter(limit=2, window=10, clock=clock)
    rl.allow("a"); rl.allow("a")
    assert not rl.allow("a").allowed 
    clock.advance(10)
    assert rl.allow("a").allowed 

def test_keys_are_independent(clock):
    rl = FixedWindowLimiter(limit=1, window=10, clock=clock)
    assert rl.allow("a").allowed
    assert rl.allow("b").allowed


def test_boundary_burst_flaw():
    """Documents the known weakness: 2x the limit within ~1 second."""
    clock = FakeClock(start=9.0)  # last second of window [0, 10)
    rl = FixedWindowLimiter(limit=5, window=10, clock=clock)
    assert all(rl.allow("a").allowed for _ in range(5))
    clock.advance(1.0)           # time is now 10, a brand new window
    assert all(rl.allow("a").allowed for _ in range(5))
