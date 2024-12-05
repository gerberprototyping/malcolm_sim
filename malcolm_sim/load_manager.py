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

    def sim_time_slice(self, time_slice:float) -> Tuple[List[Task],List[Task]]:
        """
        Simulate Load Manager for time_slice milliseconds.
        Returns a tuple containing a list of accepted and forwarded tasks.
        """
        raise NotImplementedError()
