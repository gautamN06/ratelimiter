import time 
from dataclasses import dataclass 
from typing import Callable, Protocol 


@dataclass 
class Result: 
    allowed: bool 
    remaining: int  #the requests left in curr window
    retry_after: float  #seconds until retry 


class RateLimiter(Protocol):
    def allow(self, key: str) -> Result: ... 

Clock = Callable[[], float]
default_clock = Clock = time.monotonic 



