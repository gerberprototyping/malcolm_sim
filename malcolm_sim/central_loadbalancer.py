"""This file contains malcolm_sim.CentralLoadbalancer"""

from __future__ import annotations

import logging
from typing import List

from .task import Task


class CentralLoadbalancer:
    """Central Loadbalancer to distribute tasks among Malcolm Nodes"""

    logger = logging.getLogger("malcolm_sim.CentralLoadbalancer")

    round_robin:int = 0

    @classmethod
    def distribute(cls, num_nodes:int, tasks:List[Task]) -> List[List[Task]]:
        """Distribute tasks among Malcolm Nodes"""
        if cls.round_robin >= num_nodes:
            cls.round_robin = num_nodes
        rval = [[] for _ in range(num_nodes)]
        for i in range(num_nodes):
            rval[cls.round_robin].append(tasks[i])
            cls.round_robin +=1
            if cls.round_robin >= num_nodes:
                cls.round_robin = 1
