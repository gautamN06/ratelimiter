from ratelimiter.base import Result, default_clock


class FixedWindowLimiter:
    def __init__(self, limit, window, clock=default_clock):
        self.limit = limit 
        self.window = window 
        self.clock = clock 
        self.requests = {}

    def allow(self, key):
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

        if count < self.limit:
            count += 1
            allowed = True 
        else:
            allowed = False 

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