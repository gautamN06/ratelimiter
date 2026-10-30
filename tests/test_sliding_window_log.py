from ratelimiter.sliding_window_log import SlidingWindowLogLimiter
from tests.conftest import FakeClock


def test_allows_up_to_limit_then_blocks(clock):
    rl = SlidingWindowLogLimiter(limit=3, window=10, clock=clock)
    for _ in range(3):
        assert rl.allow("a").allowed
    blocked = rl.allow("a")
    assert not blocked.allowed
    assert blocked.remaining == 0


def test_no_boundary_burst():
    """The scenario that broke fixed window now holds."""
    clock = FakeClock(start=9.0)
    rl = SlidingWindowLogLimiter(limit=5, window=10, clock=clock)
    assert all(rl.allow("a").allowed for _ in range(5))
    clock.advance(1.0)
    assert not rl.allow("a").allowed


def test_old_requests_expire_gradually(clock):
    rl = SlidingWindowLogLimiter(limit=2, window=10, clock=clock)
    rl.allow("a")                 # t=0
    clock.advance(5)
    rl.allow("a")                 # t=5
    blocked = rl.allow("a")       # t=5, full
    assert not blocked.allowed
    assert blocked.retry_after == 5   # the t=0 request expires at t=10
    clock.advance(5)              # t=10
    assert rl.allow("a").allowed  # only the t=5 request remains


def test_blocked_requests_are_not_recorded(clock):
    rl = SlidingWindowLogLimiter(limit=1, window=10, clock=clock)
    assert rl.allow("a").allowed      # t=0
    clock.advance(1)
    assert not rl.allow("a").allowed  # t=1, blocked
    clock.advance(9)                  # t=10
    assert rl.allow("a").allowed      # blocked request must not count


def test_keys_are_independent(clock):
    rl = SlidingWindowLogLimiter(limit=1, window=10, clock=clock)
    assert rl.allow("a").allowed
    assert rl.allow("b").allowed