from ratelimiter.base import Result, default_clock


class FixedWindowLimiter:
    def __init__(self, limit, window, clock=default_clock):
        if limit <= 0 or window <= 0:
            raise ValueError("limit and window must be positive")

        self.limit = limit 
        self.window = window 
        self.clock = clock 
        self.requests = {}

    def allow(self, key) -> Result: 
        #getting current time and window
        now = self.clock()
        window_id = int(now // self.window)
        stored = self.requests.get(key)

        #reset count if new window 
        if stored is None or stored[0] != window_id:
            count = 0
        else:
            count = stored[1]

        #check if request is allowed

        allowed = count < self.limit 

        if allowed: 
            count += 1 

        #calc reamining requests 

        remaining = max(0, self.limit - count)

        #save updated window and count
        self.requests[key] = (window_id, count)

        if allowed:
            retry_after = 0.0
        else:
            retry_after = (window_id + 1) * self.window - now 


        return Result(
            allowed=allowed,
            remaining=remaining,
            retry_after=retry_after
        )