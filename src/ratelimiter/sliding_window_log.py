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
        