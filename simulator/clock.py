class Clock:
    _cycle: int

    def __init__(self):
        self._cycle = 0  # current cycle
    
    def tick(self):
        self._cycle += 1
    
    def time(self):
        return self._cycle
