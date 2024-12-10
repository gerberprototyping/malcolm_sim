"""Contains malcolm_sim.PolicyOptimizer"""

from __future__ import annotations

import logging
from typing import List, Tuple

from .task import Task


class LoadManager:
    """Contains the DLB game to distribute tasks to other nodes"""

    def __init__(self, name:(str|int)) -> None:
        self.name = str(name)
        self.accept:float = 1.0
        self.forward:float = 0.0
        self.logger = logging.getLogger(f"malcolm_sim.MalcolmNode.LoadManager:{self.name}")
    
    def sim_time_slice(self, time_slice:float) -> Tuple[List[Task],List[Task]]:
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
        raise NotImplementedError()
                    