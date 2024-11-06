"""Contains malcolm_sim.Heartbeat dataclass"""

from __future__ import annotations

from dataclasses import dataclass

from .network import Network

HEARTBEAT_SIZE:int = 256


@dataclass
class Heartbeat:
    """Malcolm Node status packet"""
    availability:float
    queue_size:int

    @classmethod
    def make_packet(cls, src:str, availability:float, queue_size:int) -> Network.Packet:
        """Create a Heartbeat and embed it in a network packet"""
        data = cls(availability, queue_size)
        return Network.Packet(data, HEARTBEAT_SIZE, src, "Heartbeat", None)
