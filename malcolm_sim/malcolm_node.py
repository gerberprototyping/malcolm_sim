"""Contains the malcolm_sim.MalcolmNode class"""

from __future__ import annotations

import logging
from typing import Dict, List

from .network import Network
from .heartbeat import Heartbeat
from .schedular import Schedular


class MalcolmNode:
    """
    A Malcolm Node contains the following primary components:
    - Intra-node Schedular
    - Load Manager (DLB game)
    - Policy Optimizer
    - Network Subsystem
    """

    logger = logging.getLogger("malcolm_sim.MalcolmNode")

    all_nodes:Dict[MalcolmNode] = {}


    def __init__(self,
                 name:(str|int),
                 core_count:int,
                 core_perf:float,
                 io_count:int,
                 io_perf:float,
                 schedular_overhead:float,
                 bandwidth:int
    ) -> None:
        """This init method is not thread-safe. Init all Malcolm Nodes in same thread"""
        self.name:str = str(name)
        if self.name in self.all_nodes:
            msg = f"Malcolm Node with name '{self.name}' already exists"
            self.logger.critical(msg)
            raise ValueError(msg)
        self.src = f"MalcolmNode:{self.name}"
        self.schedular = Schedular(
            f"{name}.Schedular",
            core_count,
            core_perf,
            io_count,
            io_perf,
            schedular_overhead
        )
        # TODO: Load Manager
        # TODO: Policy Optimizer
        self.network = Network(bandwidth)
        self.other_heartbeats:Dict[Heartbeat] = {}
        self.all_nodes[self.name] = self


    def get_heartbeat_packet(self) -> Network.Packet:
        """Get a heartbeat from this node and wrap it in a network packet (thread-safe)"""
        queue_size = len(self.schedular.queue) + len(self.schedular.io_queue)
        return Heartbeat.make_packet(self.src, self.schedular.availability(), queue_size)


    def recv_packets(self, packets:List[Network.Packet]) -> None:
        """Receives packets into this malcolm node (thread-safe)"""
        new_tasks = []
        for packet in packets:
            if "Heartbeat" == packet.type:
                if not packet.src in self.all_nodes:
                    self.logger.error(
                        "MalcolmNode:%s : Received heartbeat from unknown source '%s'",
                        self.name, packet.src
                    )
                else:
                    self.other_heartbeats[packet.src] = packet.data
            elif "Task" == packet.type:
                new_tasks.append(packet.data)
            else:
                self.logger.error(
                    "MalcolmNode:%s : Unknown packet type '%s' (src=%s,attrs=%s)",
                    self.name, packet.type, packet.src, str(packet.attrs)
                )
        if new_tasks:
            self.schedular.add_tasks(new_tasks)


    def sim_time_slice(self, time_slice:float) -> Dict[str, List[Network.Packet]]:
        """Simulate a time slice on this Malcolm Node and return outgoing packets"""
        rval = {"__all__": []}
        for dest in [node.name for node in self.all_nodes]:
            rval[dest] = []
        #TODO
        rval["__all__"].append(self.get_heartbeat_packet())
        return rval
