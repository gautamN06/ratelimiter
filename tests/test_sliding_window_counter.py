from ratelimiter.sliding_window_counter import SlidingWindowCounterLimiter
from tests.conftest import FakeClock


def test_allows_up_to_limit_then_blocks(clock):
    rl = SlidingWindowCounterLimiter(limit=10, window=10, clock=clock)
    for _ in range(10):
        assert rl.allow("a").allowed
    blocked = rl.allow("a")
    assert not blocked.allowed
    assert blocked.remaining == 0


def test_previous_window_is_weighted():
    clock = FakeClock(start=5.0)
    rl = SlidingWindowCounterLimiter(limit=10, window=10, clock=clock)
    for _ in range(10):
        assert rl.allow("a").allowed      # fills window 0
    clock.advance(10)                     # t=15: halfway through window 1
    # previous window counts 10 * 0.5 = 5, so only 5 more fit
    allowed = 0
    while rl.allow("a").allowed:
        allowed += 1
    assert allowed == 5


def test_no_boundary_burst():
    clock = FakeClock(start=9.0)
    rl = SlidingWindowCounterLimiter(limit=5, window=10, clock=clock)
    assert all(rl.allow("a").allowed for _ in range(5))
    clock.advance(1.0)                    # t=10: new window, but the old one still counts fully
    assert not rl.allow("a").allowed


def test_gap_of_two_windows_resets():
    clock = FakeClock(start=5.0)
    rl = SlidingWindowCounterLimiter(limit=10, window=10, clock=clock)
    for _ in range(10):
        rl.allow("a")
    clock.advance(20)                     # t=25: window 2, previous window (1) was empty
    assert all(rl.allow("a").allowed for _ in range(10))


def test_blocked_retry_after_is_sane(clock):
    rl = SlidingWindowCounterLimiter(limit=2, window=10, clock=clock)
    rl.allow("a"); rl.allow("a")
    blocked = rl.allow("a")
    assert 0 < blocked.retry_after <= 10


def test_keys_are_independent(clock):
    rl = SlidingWindowCounterLimiter(limit=1, window=10, clock=clock)
    assert rl.allow("a").allowed
    assert rl.allow("b").allowed