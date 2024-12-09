"""Contains malcolm_sim.PolicyOptimizer"""

from __future__ import annotations

import logging
from typing import List, Tuple

from .task import Task


class LoadManager:
    """Contains the DLB game to distribute tasks to other nodes"""

    def __init__(self, name:(str|int)) -> None:
        self.name = str(name)
        self.logger = logging.getLogger(f"malcolm_sim.MalcolmNode.LoadManager:{self.name}")

    # x = states, a = actions, r = round
    def utility(x, a, r):
        print(x)

    def value(strat):
        print(strat)

    def nash_equilibrium():
        print("nash")

    def sim_time_slice(self, time_slice:float) -> Tuple[List[Task],List[Task]]:
        """
        Simulate Load Manager for time_slice milliseconds.
        Returns a tuple containing a list of accepted and forwarded tasks.

        N nodes
        node i receives a new task with probability p_i and completes one with q_i
        load on node i at round r is x_ir
        the state at round r is x_r = (x_ir, ... , x_Nr)
        scheduling actions by agent i at round r is a_ir for example a_ir = {accept, steal from j}
        aggregate all actions taken by all nodes at roudn r as a_r = (a_1r, ..., a_Nr)
        strategy of agent i strat_i and strat_-i all other agent strategies

        """
        curr_time:float = 0
        while curr_time < time_slice:
            print(curr_time)
            curr_time += 1
        return [[1],[2]]
