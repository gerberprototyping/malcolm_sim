"""Contains the malcolm_sim.MalcolmNode class"""

from __future__ import annotations

import logging
import re
import threading
from typing import Callable, Dict, List

from .load_manager import LoadManager
from .policy_optimizer import PolicyOptimizer
from .network import Network
from .heartbeat import Heartbeat
from .schedular import Schedular
from .task import Task
from .thread_safe_list import ThreadSafeList


TIMEOUT = 20
TIMEOUT_MSG = "Dead-lock detected"


class MalcolmNode:
    """
    A Malcolm Node contains the following primary components:
    - Intra-node Schedular
    - Load Manager (DLB game)
    - Policy Optimizer
    - Network Subsystem
    """

    logger = logging.getLogger("malcolm_sim.MalcolmNode")

    # List of all instantiated nodes
    all_nodes:Dict[str,MalcolmNode] = {}

    # Multi-thread locks and callback
    start_time_slice:threading.Event = threading.Event()
    barrier:threading.Barrier = None
    async_callback:Callable = None


    @classmethod
    def _async_callback(cls) -> None:
        if callable(cls.async_callback):
            cls.async_callback()        # pylint: disable=not-callable


    @classmethod
    def set_async_callback(cls, callback:Callable) -> None:
        """Set the callback to be run after each time slice when running async"""
        cls.async_callback = callback


    @classmethod
    def from_config(cls, node_config:dict) -> MalcolmNode:
        """Create a Malcolm Node from config dict. Assumes schema is validated"""
        defaults = {
            "core_perf": 1,
            "io_perf": 1,
        }
        for k,v in defaults.items():
            if k not in node_config:
                node_config[k] = v
        return cls(**node_config)


    def __init__(self,
                 name:(str|int),
                 core_count:int,
                 core_perf:float,
                 io_count:int,
                 io_perf:float,
                 overhead:float,
                 bandwidth:int
    ) -> None:
        """
        This init method is not thread-safe. Init all Malcolm Nodes in same
        thread before starting
        """
        self.name:str = str(name)
        if self.name in self.all_nodes:
            msg = f"Malcolm Node with name '{self.name}' already exists"
            self.logger.critical(msg)
            raise ValueError(msg)
        self.src = f"MalcolmNode:{self.name}"
        #Init Load Manager
        self.load_manager = LoadManager(self.name)
        # Init Policy Optimizer
        self.policy_optimizer = PolicyOptimizer(self.name, self)
        # Init Schedular
        self.schedular = Schedular(
            self.name,
            core_count,
            core_perf,
            io_count,
            io_perf,
            overhead
        )
        # Init Network
        self.network = Network(bandwidth)
        # Init internal lists
        self.task_inbox:ThreadSafeList[Task] = ThreadSafeList()
        self.tx_queue:List[Network.Packet] = []
        self.other_heartbeats:Dict[Heartbeat] = {}
        self.latency:float = 0
        # Add self to list of nodes
        self.all_nodes[self.name] = self
        self.barrier = threading.Barrier(
            len(self.all_nodes) + 1,        # Number of nodes plus one main main thread
            action=self._async_callback,
            timeout=TIMEOUT
        )


    def get_heartbeat_packet(self, dest:str) -> Network.Packet:
        """Get a heartbeat from this node and wrap it in a network packet (thread-safe)"""
        queue_size = len(self.schedular.queue) + len(self.schedular.io_queue)
        return Heartbeat.make_packet(self.src, dest, self.schedular.expected_performance(), queue_size)


    def recv_packets(self, packets:List[Network.Packet]) -> None:
        """Receives packets into this malcolm node (thread-safe)"""
        new_tasks:List[Task] = []
        for packet in packets:
            if "Heartbeat" == packet.type:
                src = packet.src.split(":")[1]
                if not src in list(self.all_nodes.keys()):
                    self.logger.error(
                        "MalcolmNode:%s : Received heartbeat from unknown source '%s'",
                        self.name, src
                    )
                else:
                    self.other_heartbeats[src] = packet.data
            elif "Task" == packet.type:
                new_tasks.append(packet.data)
            else:
                self.logger.error(
                    "MalcolmNode:%s : Unknown packet type '%s' (src=%s,attrs=%s)",
                    self.name, packet.type, src, str(packet.attrs)
                )
        if new_tasks:
            self.task_inbox.extend(new_tasks)


    @classmethod
    def route_packets(cls, packets:List[Network.Packet]) -> None:
        """Route network packets to the destination MalcolmNode (thread-safe)"""
        if not packets:
            return
        routed_packets = {}
        for node_name in cls.all_nodes:
            routed_packets[node_name] = []
        for packet in packets:
            if match := re.match(r"^MalcolmNode:(.*)", packet.dest):
                dest_node = match.group(1)
                if dest_node in cls.all_nodes:
                    routed_packets[dest_node].append(packet)
                else:
                    cls.logger.error(
                        "MalcolmNode.route_packets : Invalid packet destination '%s'. Node does not exist",
                        packet.dest
                    )
            else:
                cls.logger.error(
                    "MalcolmNode.route_packets : Invalid packet destination '%s'. Should start with 'MalcolmNode:'",
                    packet.dest
                )
        for node_name,node_packets in routed_packets.items():
            cls.all_nodes[node_name].recv_packets(node_packets)


    def sim_time_slice(self, time_slice:float, curr_time:float) -> List[Network.Packet]:
        """"
        Simulate time slice on this Malcolm Node (NOT thread-safe)
        """
        # Run Policy Optimizer
        self.policy_optimizer.sim_time_slice(time_slice, self.load_manager)

        # Run Load Manager (returns accepted and forwarded tasks)
        accepted:List[Task]
        forwarded:List[Network.Packet] = []
        accepted,forwarded = self.load_manager.sim_time_slice(time_slice, self.task_inbox.as_list())
        self.task_inbox.clear()

        # Send accepted tasks to Schedular and simulate
        self.schedular.add_tasks(accepted)
        completed = self.schedular.sim_time_slice(time_slice)
        self.latency = 0
        if completed:
            for task in completed:
                x = curr_time - task.attrs["gen_time"]
                task.attrs["latency"] = x
                self.latency += x
            self.latency /= len(completed)

        # Prepare outgoing packets
        for node_name in self.all_nodes:    # heartbeat packets sent first
            if node_name != self.name:
                dest = f"MalcolmNode:{node_name}"
                self.tx_queue.append(self.get_heartbeat_packet(dest))
        self.tx_queue.extend(forwarded)

        # Throttle outgoing packets via Network subsystem
        rval,self.tx_queue = self.network.sim_time_slice(time_slice, self.tx_queue)
        return rval


    def run_async(self, time_slice:float, sim_time:float) -> None:
        """This method should be used as the entry point when running multi-threaded"""
        curr_time:float = 0.0
        while curr_time <= sim_time:
            # Wait for new tasks to be generated
            if not self.start_time_slice.wait(TIMEOUT):
                raise TimeoutError(TIMEOUT_MSG)
            # Simulate time slice
            packets = self.sim_time_slice(time_slice, curr_time)       # properly synchronized
            # Wait for all nodes to finish time slice
            self.barrier.wait(TIMEOUT)
            curr_time += time_slice
            # Route packets
            self.route_packets(packets)
            # Wait for all nodes again
            self.barrier.wait(TIMEOUT)


    @classmethod
    def run_all_async(cls, time_slice:float, task_gen:Callable) -> None:
        """
        Run multi-threaded simulation of all nodes. The task_gen callable
        should return the
        """
