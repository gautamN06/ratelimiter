from ratelimiter.base import Result, default_clock

class SlidingWindowCounterLimiter:
    def __init__(self, limit: int, window: float, clock=default_clock):
        if limit <= 0 or window <= 0:
            raise ValueError("limit and window must be positive")

        self.limit = limit 
        self.window = window 
        self.clock = clock 
        self.requests = {}

    def allow(self, key: str) -> Result:
        now = self.clock()
        window_id = int(now // self.window)

        stored = self.requests.get(key)

        if stored is None:
            current_count = 0
            previous_count = 0

        else:
            stored_window, stored_current, stored_previous = stored

            # still in same window 
            if stored_window == window_id: 
                current_count = stored_current
                previous_count = stored_previous

            # moved foreward one window 
            elif stored_window == window_id - 1: 
                current_count = 0 
                previous_count = stored_current

            #skipped more than one window 
            else:
                current_count = 0 
                previous_count = 0 

            #calc the weighted request count 
        elapsed = now - (window_id * self.window)
        elapsed_fraction = elapsed / self.window 

        estimated_count = (
            previous_count * (1 - elapsed_fraction) + current_count
        )

        #determining whether request should be allowed 

        if estimated_count < self.limit:
            current_count += 1
            allowed = True 
        else:
            allowed = False 

        #calculating remaining requests 
        remaining = max(0, int(self.limit - estimated_count - (1 if allowed else 0)))


        #retry time 
        if allowed:
            retry_after = 0.0
        else:
            retry_after = self.window - elapsed 

        #save updated coutns 
        self.requests[key] = (
            window_id, 
            current_count, 
            previous_count
        )

        return Result(
            allowed=allowed,
            remaining=remaining,
            retry_after=retry_after
        )