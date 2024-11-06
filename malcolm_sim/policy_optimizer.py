"""Contains malcolm_sim.PolicyOptimizer"""

from __future__ import annotations

from .schedular import Schedular
from .network import Network


class PolicyOptimizer:
    """Tracks heartbeats from other Nodes sends adjustments to the Load Manager"""

    def __init__(self, schedular:Schedular) -> None:
        self.schedular = schedular

    def get_heartbeat(self) -> Network.Packet:
        """Generate heartbeat network packet"""
