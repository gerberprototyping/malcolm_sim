"""Contains malcolm_sim.Heartbeat dataclass"""

from __future__ import annotations

from dataclasses import dataclass

from .network import Network

HEARTBEAT_SIZE:int = 256


@dataclass
class Heartbeat:
    """Malcolm Node status packet"""
    expected_performance:float
    queue_size:int

    @classmethod
    def make_packet(cls, src:str, dest:str, expected_performance:float, queue_size:int) -> Network.Packet:
        """Create a Heartbeat and embed it in a network packet"""
        data = cls(expected_performance, queue_size)
        return Network.Packet(data, HEARTBEAT_SIZE, src, dest, "Heartbeat", None)
