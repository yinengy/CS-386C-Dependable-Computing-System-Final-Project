from __future__ import annotations
from typing import List, TYPE_CHECKING
from queue import Queue
from abc import ABC, abstractmethod

from .message import Message

if TYPE_CHECKING:
    from .clock import Clock

class Processor(ABC):
    def __init__(self, id: int, clock: Clock):
        """
        id: processor id, start from 0
        clock: a shared global clock object (for simplicity)
        """
        self.id = id
        self._outbound_msgs = Queue()
        self._inbound_msgs = Queue()
        self._scheduled_msgs = []
        self._clock = clock

    def send_datagram(self, dst: int, text: str, deadline: int):
        """
        Send message to one processor
        """
        msg = Message.datagram_msg(self.id, dst, text, self._clock.time(), deadline)
        self._outbound_msgs.put(msg)
        print(f"proc {self.id}: -> send {msg} to proc {dst}")

    def broadcast(self, text: str, deadline: int):
        """
        Send message to all processors
        """
        msg = Message.broadcast_msg(self.id, text, self._clock.time(), deadline)
        self._outbound_msgs.put(msg)
        print(f"proc {self.id}: -> broadcast {msg}")

    def add_incoming_message(self, msg: Message):
        """
        Get message from network
        """
        self._inbound_msgs.put(msg)

    def dequeue_outbound_msgs(self) -> List[Message]:
        """
        Get all outbound msgs and reset the queue
        """
        ret = list(self._outbound_msgs.queue)
        self._outbound_msgs = Queue()
        return ret

    def dequeue_inbound_msg(self) -> Message:
        """
        Get one inbound msg and remove it from the queue
        Return None if no inbound msg
        """
        if self._inbound_msgs.empty():
            return None
        
        return self._inbound_msgs.get()

    def schedule_broadcast(self, text: str, deadline: int, schedule_time: int):
        """
        Schedule a broadcast message to be sent at time
        """
        msg = Message.broadcast_msg(self.id, text, schedule_time, deadline)
        self._scheduled_msgs.append(msg)

    def cancel_schedule(self):
        """
        Cancel all scheduled messages
        """
        self._scheduled_msgs = []

    @abstractmethod
    def next_cycle(self) -> None:
        """
        This function shoule be overrided by user
        Which should prepare and processing messages
        """
        print("Processor.next_cycle() Not Implemented!")
