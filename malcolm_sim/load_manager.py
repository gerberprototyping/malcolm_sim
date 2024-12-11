"""Contains malcolm_sim.PolicyOptimizer"""

from __future__ import annotations

import logging
import numpy as np
from typing import List, Tuple

from .network import Network

from .task import Task


class LoadManager:
    """Contains the DLB game to distribute tasks to other nodes"""

    def __init__(self, name:(str|int)) -> None:
        self.name = str(name)
        self.accept:float = 1.0
        self.forward:float = 0.0
        self.src:str = None
        self.dest:str = "MalcolmNode:Node0"
        self.logger = logging.getLogger(f"malcolm_sim.MalcolmNode.LoadManager:{self.name}")
    
    def sim_time_slice(self, time_slice:float, incoming_tasks:List[Task]) -> Tuple[List[Task],List[Network.Packet]]:
        """
        Simulate Load Manager for time_slice milliseconds.
        Returns a tuple containing a list of accepted and forwarded tasks.

        N nodes
        node i receives a new task with probability p_i and completes one with q_i
        load on node i at round r is x_ir
            - the load is found by computing the length of the queue and the time that a node takes to complete a task
        the state at round r is x_r = (x_ir, ... , x_Nr)
        scheduling actions by agent i at round r is a_ir for example a_ir = {accept, steal from j}
        aggregate all actions taken by all nodes at roudn r as a_r = (a_1r, ..., a_Nr)
        strategy of agent i as strat_i and strat_-i for all other agent strategies

        """
        actions = ["accept","forward"]
        accepted:List[Task] = []
        forwarded:List[Task] = []
        for task in incoming_tasks:
            action = np.random.choice(actions, p=[self.accept, self.forward])
            if action == "accept":
                self.logger.debug(f"With {self.accept} Accepted task: {task}")
                accepted.append(task)
            elif action == "forward":
                self.logger.debug(f"With {self.forward} Forwarded task: {task}")
                forwarded.append(task)
        forwarded_packets = []
        for task in forwarded:
            forwarded_packets.append(task.make_packet(self.src, self.dest))
        return accepted, forwarded_packets
                    