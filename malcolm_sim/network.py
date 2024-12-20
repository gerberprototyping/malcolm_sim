"""Contains the malcolm_sim.Network class"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


class Network:
    """Network subsystem to limit outgoing bandwidth"""

    @dataclass
    class Packet:
        """Network packet object. Just a wrapper around the attribute 'data'"""
        data:any
        size:int
        src:str
        dest:str
        type:str
        attrs:dict

    def __init__(self, bandwidth:int) -> None:
        """Bandwidth is measured in bits/s"""
        self.bandwidth = bandwidth
        self.utilization:float = 0

    def sim_time_slice(self, time_slice:float, packets:Iterable[Packet]) \
        -> Tuple[List[Packet], List[Packet]]:
        """
        Limit outgoing bandwidth. First return element is sent packets, second
        are throttled packets (NOT thread-safe)
        """
        send = []
        throttle = []
        limit = int((self.bandwidth/8)*time_slice*1000)
        count = 0
        self.utilization = 8*sum([packet.size for packet in packets])
        for packet in packets:
            if count+packet.size <= limit:
                send.append(packet)
            else:
                throttle.append(packet)
        return (send, throttle)

    def availability(self) -> int:
        """Returns the unutilized bandwidth of the interface in bits/s (NOT thread-safe)"""
        return self.bandwidth - self.utilization
