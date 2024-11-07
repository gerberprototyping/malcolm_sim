"""Contains the primary class for the malcolm_sim module"""

import logging
import threading
from typing import Callable, List

from .central_loadbalancer import CentralLoadBalancer
from .malcolm_node import MalcolmNode
from .schedular import Schedular
from .task import Task
from .log import get_main_logger


TIMEOUT = 20


class MalcolmSim:
    """Primary class of the malcolm_sim module. Allows simulating a Malcolm Cluster"""

    logger:logging.Logger = get_main_logger("malcolm_sim", "malcolm_sim.log")


    def __init__(self, task_gen:Callable) -> None:
        self.task_gen = task_gen


    def run(self, time_slice:float, sim_time:float) -> None:
        """Run single-threaded simulation of this MalcolmSim instance"""
        curr_time:float = 0.0
        num_nodes = len(MalcolmNode.all_nodes)
        self.logger.info("Running simulation in single-threaded mode")
        while curr_time <= sim_time:
            self.logger.info("Simulating time slice %g ms", curr_time)
            # Generate and distribute new tasks
            new_tasks = self.task_gen(time_slice)
            MalcolmNode.route_packets(
                CentralLoadBalancer.distribute(num_nodes, new_tasks)
            )
            # Simulate time slice for all nodes
            forwarded_task_packets = []
            for node in MalcolmNode.all_nodes.values():
                forwarded_task_packets.extend(
                    node.sim_time_slice(time_slice)
                )
            # Route heartbeat and forwarded task packets
            MalcolmNode.route_packets(forwarded_task_packets)
            # TODO print interesting stuff
            curr_time += time_slice
        self.logger.info("Simulation completed")


    def run_async(self, time_slice:float, sim_time:float) -> None:
        """Run multi-threaded simulation of this MalcolmSim instance"""
        curr_time:float = 0.0
        num_nodes = len(MalcolmNode.all_nodes)
        threads:List[threading.Thread] = []
        self.logger.info("Running simulation using %d threads", num_nodes)
        MalcolmNode.start_time_slice.clear()
        # Spawn MalcolmNode threads
        for node in MalcolmNode.all_nodes.values():
            name = f"Thread-{node.src}"
            self.logger.info("Starting %s", name)
            thread = threading.Thread(
                target=MalcolmNode.run_async,
                name=name,
                args=(node, time_slice, sim_time)
            )
            thread.start()
            threads.append(thread)
        # Main simulation loop
        while curr_time <= sim_time:
            self.logger.info("Simulating time slice %g ms", curr_time)
            # Generate and distribute new tasks
            new_tasks = self.task_gen(time_slice)
            MalcolmNode.route_packets(
                CentralLoadBalancer.distribute(num_nodes, new_tasks)
            )
            # Signal nodes to start time_slice
            MalcolmNode.start_time_slice.set()
            # Wait for nodes finish time_slice
            MalcolmNode.barrier.wait(TIMEOUT)
            # Clear start event while nodes are routing packets
            MalcolmNode.start_time_slice.clear()
            # TODO print interesting stuff
            #     (no not access MalcolmNode incoming_tasks or other_heartbeats)
            # Wait for all nodes again
            MalcolmNode.barrier.wait(TIMEOUT)
        # Wait for all threads
        self.logger.info("")
        for thread in threads:
            print(f"Waiting for {thread.getName()}", end="\r")
            thread.join()
        print("All threads terminated"+" "*64)
        self.logger.info("Simulation completed")


    @classmethod
    def _test_schedular(cls) -> None:
        """Internal testing method"""
        # cls.logger.setLevel(logging.INFO)
        cls.logger.setLevel(logging.DEBUG)
        # cls.logger.setLevel(logging.TRACE)
        time_slice = 1
        tasks = [
            Task("#0", 1, 0, 128),
            Task("#1", 2, 0, 128),
            Task("#2", 1, 0, 128),
            Task("#3", 8, 2, 128),
            Task("#4", 1, 2, 128),
            Task("#5", 1, 2, 128),
        ]
        schedular = Schedular(
            name="Testing",
            core_count=2,
            core_perf=1,
            io_count=32,
            io_perf=1,
            overhead=0
        )
        schedular.add_tasks(tasks)
        print(schedular)
        print()
        print("Tasks:")
        for task in tasks:
            print("    " + task.short_str())
        print()
        print("="*50)

        for t in range(1, 25+1):
            print()
            print()
            print("-"*50)
            print(f"Time {t:3d} ms")
            print()
            completed = schedular.sim_time_slice(time_slice)
            if completed and cls.logger.level > logging.INFO:
                print(f"Completed the following tasks at time {t} ms")
                for task in completed:
                    print(f"    - {task.name}")

        # print(schedular.get_load())
