from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING

from simulator.processor import Processor

if TYPE_CHECKING:
    from simulator.clock import Clock

class Config:
    num_proc = 3
    datagram_latency = 2
    broadcast_latency = 2
    period = 10

class Failure:
    processor_fault_gap = 10 # minimum gap between two failure
    processor_fault_chance = 0.1 # chance of a failure for every cycle

    

class AttendanceListProcessor(Processor):
    # text type
    LIST = 0
    NEWGROUP = 1
    PRESENT = 2

    def __init__(self, id: int, clock: Clock):
        super().__init__(id, clock)
        self._members = []
        self.received_list = False  # Have I recived a list in this period?
        self.group_inited_time = 0
        self.found_error = False

    def _generate_list(self, prev_list: List[int]) -> str:
        """
        text format: "LIST:0,1,2" or "LIST:" or "LIST:0"
        """
        prev_list.append(self.id)

        return "LIST:" + ",".join([str(n) for n in prev_list])

    def _generate_present(self):
        """
        text format: "PRESENT:"
        """
        return "PRESENT:"

    def _generate_newgroup(self):
        """
        text format: "NEWGROUP:"
        """
        return "NEWGROUP:"

    @staticmethod
    def _parse_list(text: str) -> List[int]:
        """
        text format: "0,1,2" or "" or "0"
        """
        if text == "":
            return []

        return [int(s) for s in text.split(",")] 

    @staticmethod
    def _parse_text(text: str) -> Tuple[int, str]:
        assert(":" in text)
        header_str, *body_str = text.split(":")

        header = None
        body = None
        if header_str == "LIST":
            header = AttendanceListProcessor.LIST
            body = AttendanceListProcessor._parse_list(body_str[0])
        elif header_str == "NEWGROUP":
            header = AttendanceListProcessor.NEWGROUP
            body = None
        elif header_str == "PRESENT":
            header = AttendanceListProcessor.PRESENT
            body = None
        else:
            raise RuntimeError("Invalid message: {}", text)
        
        return header, body

    def is_last_member(self) -> bool:
        """
        True if self.id is the last one in members
        """
        assert(len(self._members) > 1)
        return self._members[-1] == self.id

    def is_first_member(self) -> bool:
        """
        True if self.id is the frist one in members
        """
        assert(len(self._members) > 1)
        return self._members[0] == self.id


    def next_member(self):
        """
        Return the id of the member next to self.id

        Do not call this if self.id is the last memeber
        """
        return self._members[self._members.index(self.id) + 1]

    def next_cycle(self) -> None:
        current_time = self._clock.time()
        msg = None
        
        while True:
            # scheduled task
            if current_time == 0 and self.id == 0:
                text = self._generate_newgroup()
                self.broadcast(text, current_time + Config.broadcast_latency)
                self._members = [self.id]
            elif len(self._members) < 2:
                pass  # haven't form a valid member list
            elif self.is_first_member():
                if (current_time - self.group_inited_time) % Config.period == 0:
                    if self.received_list: # last period is safe
                        self.received_list = False
                        text = self._generate_list([])
                        self.send_datagram(self.next_member(), text, current_time + Config.datagram_latency)
                    else: # didn't recieve message from the last member on time
                        self.found_error = True
                        text = self._generate_newgroup()
                        self.broadcast(text, current_time + Config.broadcast_latency)
                        self.group_inited_time = current_time
                        self._members = [self.id]
            else:  # other memebers
                if not self.found_error and len(self._members) > 1:
                    if not self.received_list:  
                        index = self._members.index(self.id)
                        if (current_time - self.group_inited_time) % Config.period > (index * Config.datagram_latency):
                            self.found_error = True
                            text = self._generate_newgroup()
                            self.broadcast(text, current_time + Config.broadcast_latency)
                            self.group_inited_time = current_time
                            self._members = [self.id]
                if (current_time - self.group_inited_time) % Config.period == 0:
                    self.received_list = False # a new period
                    self.found_error = False

            msg = self.dequeue_inbound_msg()
            if msg is None:
                break # no message

            # discard message if it is delayed
            if current_time > msg.deadline:
                continue

            header, body = AttendanceListProcessor._parse_text(msg.text)

            print(f"proc {self.id}: <- recv {msg} from proc {msg.src}")

            if header == AttendanceListProcessor.LIST:
                text = self._generate_list(body)
                if self.is_first_member():
                    pass
                elif not self.is_last_member():
                    self.send_datagram(self.next_member(), text, current_time + Config.datagram_latency)
                else:
                    self.send_datagram(self._members[0], text, current_time + Config.datagram_latency)
                self.received_list = True
            elif header == AttendanceListProcessor.NEWGROUP:
                self.found_error = True
                text = self._generate_present()
                self.broadcast(text, current_time + Config.broadcast_latency)

                # prepare to build a new member list
                self._members = [msg.src, self.id]
                self._members.sort()
            elif header == AttendanceListProcessor.PRESENT:
                self._members.append(msg.src)
                self._members.sort()
                self.received_list = True

                