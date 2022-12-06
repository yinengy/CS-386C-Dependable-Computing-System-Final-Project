from __future__ import annotations
from typing import List, TYPE_CHECKING
import random

from .message import Message

if TYPE_CHECKING:
    from .processor import Processor
    from .clock import Clock

random.seed(10)

class Network:
    _bus: List[Message]

    def __init__(self, clock: Clock, proc_list: List[Processor], failure: "Failure") -> None:
        self._bus = []
        self._clock = clock
        self._proc_list = proc_list
        self._last_failure = 0
        self._failed_proc = []
        self._failure = failure

    def push(self, msg: Message):
        """
        Add a msg into bus
        """
        self._bus.append(msg)

    def next_cycle(self):
        """
        Countdown all message's delay_countdown by 1
        Deliver message if it is ready (delay_countdown == 0)

        Then add outbound messages from all processors to bus
        """
        new_bus = []

        # generate processor failure
        if self._failure is not None and len(self._proc_list) - len(self._failed_proc) > 2:  # should have at least two alive proc
            if self._last_failure + self._failure.processor_fault_gap < self._clock.time(): # gap between failures has reached
                if random.random() <= self._failure.processor_fault_chance: # triggered a proc fault
                    proc_id = random.choice([n for n in self._proc_list if n not in self._failed_proc])
                    self._failed_proc.append(proc_id)
                    self._last_failure = self._clock.time()
                    print(f"proc {proc_id.id}: failed!!!!!!")

        # deliver old messages
        for msg in self._bus:
            if msg.count_down():
                if msg.type == Message.DATAGRAM:
                    self._proc_list[msg.dst].add_incoming_message(msg)
                else:
                    for proc in self._proc_list:
                        if proc.id != msg.src:
                            proc.add_incoming_message(msg)
            else:
                new_bus.append(msg)

        # add new messages
        for proc in self._proc_list:
            if proc not in self._failed_proc:
                new_bus.extend(proc.dequeue_outbound_msgs())

        # update bus status
        self._bus = new_bus
        