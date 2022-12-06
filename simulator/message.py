class Message:
    # Type
    DATAGRAM = 0
    BROADCAST = 1

    def __init__(self, type: int, timestamp: int, deadline: int, src: int = None, dst: int = None, text: str = None):
        self.type = type  # Message.DATAGRAM or Message.BROADCAST
        self.timestamp = timestamp
        self.deadline = deadline
        self.src = src
        self.dst = dst
        self.text = text
        self.delay_countdown = 2  # TODO: replace with a Delay object, shoule be at least 1

    def is_datagram(self) -> bool:
        return self.type == Message.DATAGRAM

    def is_broadcast(self) -> bool:
        return self.type == Message.BROADCAST

    @staticmethod
    def broadcast_msg(src: int, text: str, timestamp: int, deadline: int) -> "Message":
        return Message(Message.BROADCAST, timestamp, deadline, src=src, text=text)

    @staticmethod
    def datagram_msg(src: int, dst: int, text: str, timestamp: int, deadline: int) -> "Message":
        return Message(Message.DATAGRAM, timestamp, deadline, src=src, dst=dst, text=text)

    def count_down(self) -> bool:
        """
        Countdown the delay counter by one,
        Return True if the counter reaches 0
        """
        assert(self.delay_countdown >= 1)
        self.delay_countdown -= self.delay_countdown
        return self.delay_countdown == 0
    
    def __str__(self) -> str:
        return f"msg: '{self.text}'"
