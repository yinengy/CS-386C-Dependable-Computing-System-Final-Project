from __future__ import annotations
from typing import List, TYPE_CHECKING, Type

from .network import Network
from .processor import Processor
from .clock import Clock

class Simulator:
    _network: Network
    _proc_list: List[Processor]

    def __init__(self, num_proc: int, Processor_Impl: Type[Processor], failure: "Failure" = None) -> None:
        """
        Processor_Impl: A user implemented class that inherit ```Processor```
        failure: A user defined class which contains config for failure frequency
        """
        self._clock = Clock()

        # intialize processors
        assert(num_proc >= 2)
        self._proc_list = []
        for i in range(num_proc):
            self._proc_list.append(Processor_Impl(i, self._clock))
    
        self._network = Network(self._clock, self._proc_list, failure)

    def next_cycle(self):
        """
        Process to next cycle
        Will update the whole system's status
        """
        # 1. processors
        for proc in self._proc_list:
            if proc not in self._network._failed_proc:
                proc.next_cycle()

        # 2. network
        self._network.next_cycle()

        # 3. clock tick
        self._clock.tick()

        # 4: print current state
        