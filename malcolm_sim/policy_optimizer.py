"""Contains malcolm_sim.PolicyOptimizer"""

from __future__ import annotations

import logging

from .malcolm_node import MalcolmNode


class PolicyOptimizer:
    """Tracks heartbeats from other Nodes sends adjustments to the Load Manager"""

    def __init__(self, name:(str|int), node:MalcolmNode) -> None:
        self.name = str(name)
        self.node = node
        self.logger = logging.getLogger(f"malcolm_sim.MalcolmNode.LoadManager:{self.name}")

    def sim_time_slice(self, time_slice:float) -> None:
        """
        Simulate Policy Optimizer for time_slice milliseconds.
        Makes adjustments to node.load_manager based on heartbeats of other nodes
        """
        raise NotImplementedError()
