import pytest 

class FakeClock:
    def __init__(self, start: float = 0.0):
        self.now = start 

    def __call__(self) -> float: 
        return self.now 

    def advance(self, seconds: float) -> None: 
        self.now += seconds 


@pytest.fixture 
def clock():
    return FakeClock()

