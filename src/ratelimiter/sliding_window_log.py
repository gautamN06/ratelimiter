from collections import deque 
from ratelimiter.base import Result, default_clock



class SlidingWindowLogLimiter:
    def __init__(self, limit: int, window: float, clock=default_clock):
        if limit <= 0 or window <= 0:
            raise ValueError("limit and window must be positive")

        self.limit = limit 
        self.window = window 
        self.clock = clock 
        self.requests = {}


    def allow(self, key: str) -> Result:
        now = self.clock()
        timestamps = self.requests.setdefault(key,deque())

        while timestamps and timestamps[0] <= now - self.window:
            timestamps.popleft()

        if len(timestamps) < self.limit:
            timestamps.append(now)
            allowed=True
            retry_after=0.0
        else:
            allowed=False 
            retry_after = timestamps[0] + self.window - now 

        remaining = max(0, self.limit - len(timestamps))

        return Result(
            allowed=allowed,
            remaining=remaining,
            retry_after=retry_after
        )