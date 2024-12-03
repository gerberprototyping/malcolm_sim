"""This file contains malcolm_sim.CentralLoadbalancer"""

from __future__ import annotations

import logging
from typing import List

from .task import Task
from .network import Network
from .malcolm_node import MalcolmNode


class CentralLoadBalancer:
    """Central Loadbalancer to distribute tasks among Malcolm Nodes"""

    logger = logging.getLogger("malcolm_sim.CentralLoadbalancer")

    round_robin:int = 0

    @classmethod
    def distribute(cls, tasks:List[Task]) -> List[Network.Packet]:
        """Distribute tasks among Malcolm Nodes"""
        num_nodes = len(MalcolmNode.all_nodes)
        if cls.round_robin >= num_nodes:
            cls.round_robin = 0
        rval:List[Network.Packet] = []
        for task in tasks:
            node_name = list(MalcolmNode.all_nodes.keys())[cls.round_robin]
            rval.append(Network.Packet(
                data=task,
                size=task.payload,
                src="CentralLoadBalancer",
                dest=f"MalcolmNode:{node_name}",
                type="Task",
                attrs={}
            ))
            cls.round_robin +=1
            if cls.round_robin >= num_nodes:
                cls.round_robin = 0
        return rval
