"""Contains the primary class for the malcolm_sim module"""

from __future__ import annotations

import json
import logging
import threading
from typing import Dict, List

import yaml
import matplotlib.pyplot as plt
from schema import Schema, And, Or, Use, Optional

from .iec_int import IEC_Int
from .central_loadbalancer import CentralLoadBalancer
from .malcolm_node import MalcolmNode
from .schedular import Schedular
from .task import Task
from .task_gen import TaskGen
from .log import get_main_logger


TIMEOUT = 20

task_schema = Or(
    {
        "type": Or("const", "constant"),
        "value": And(Use(float), lambda n: n > 0)
    },
    {
        "type": Or("gaussian", "normal"),
        "center": And(Use(float), lambda n: n > 0),
        "scale": And(Use(float), lambda n: n > 0)
    }
)


class MalcolmSim:
    """Primary class of the malcolm_sim module. Allows simulating a Malcolm Cluster"""

    logger:logging.Logger = get_main_logger("malcolm_sim", "malcolm_sim.log")

    config_schema:Schema = Schema({
        "MalcolmNodes": [{
            "name": Use(str),
            "core_count": And(Use(IEC_Int), lambda n: n > 0),
            Optional("core_perf"): And(Use(float), lambda n: n > 0),
            "io_count": And(Use(IEC_Int), lambda n: n > 0),
            Optional("io_perf"): And(Use(float), lambda n: n > 0),
            "overhead": And(Use(float), lambda n: n >= 0),
            "bandwidth": And(Use(IEC_Int), lambda n: n > 0)
        }],
        "Tasks": {
            "rate": task_schema,
            "runtime": task_schema,
            "io_time": task_schema,
            "payload": task_schema
        }
    })


    @classmethod
    def from_json_yaml(cls, filename:str) -> None:
        """Configures the instance from a JSON or YAML file"""
        # Parse file
        ext = filename.split(".")[-1].lower()
        with open(filename, "r", encoding="utf-8") as f:
            if ext == "json":
                config = json.load(f)
            elif ext in ["yaml", "yml"]:
                config = yaml.safe_load(f)
            else:
                raise ValueError(f"The file '{filename}' is not a valid JSON or YAML file.")
        # Validate schema
        config = cls.config_schema.validate(config)
        # Parse config
        task_gen = None
        for key,value in config.items():
            key = key.lower()
            if "malcolmnodes" == key:
                for node_config in value:
                    MalcolmNode.from_config(node_config)
            elif "tasks" == key:
                task_gen = TaskGen.from_config(value)
            # else not required because schema is validated
        return cls(task_gen)


    def __init__(self, task_gen:TaskGen) -> None:
        self.task_gen = task_gen
        self.metrics:Dict[str, Dict[str, List[any]]] = {}

    def cli(self, argv) -> None:
        """Command line interface to MalcolmSim"""
        raise NotImplementedError

    def get_metrics(self) -> Dict[str, Dict[str, (float|int)]]:
        """Collect metrics from all nodes"""
        rval = {
            "CPU Util": {},
            "IO Util": {},
            "CPU Queue": {},
            "IO Queue": {},
            "Completed": {},
            "Latency": {},
        }
        for node in MalcolmNode.all_nodes.values():
            name = node.name
            rval["CPU Util"][name]  = node.schedular.core_utilization
            rval["IO Util"][name]   = node.schedular.io_utilization
            rval["CPU Queue"][name] = len(node.schedular.queue)
            rval["IO Queue"][name]  = len(node.schedular.io_queue)
            rval["Completed"][name] = node.schedular.completed
            rval["Latency"][name]   = node.latency
        return rval

    def run(self, time_slice:float, sim_time:float) -> None:
        """Run single-threaded simulation of this MalcolmSim instance"""
        curr_time:float = 0.0
        self.logger.info("Running simulation in single-threaded mode")
        self.metrics = {}
        while curr_time <= sim_time:
            self.logger.info("Simulating time slice %g ms", curr_time)
            # Generate and distribute new tasks
            new_tasks = self.task_gen.gen_time_slice(time_slice, curr_time)
            if new_tasks:
                msg = f"Generated {len(new_tasks)} new task(s)"
                for task in new_tasks:
                    msg += f"\n{task}"
                self.logger.debug(msg)
            else:
                self.logger.info("No new tasks generated this time slice")
            MalcolmNode.route_packets(
                CentralLoadBalancer.distribute(new_tasks)
            )
            # Simulate time slice for all nodes
            forwarded_task_packets = []
            for node in MalcolmNode.all_nodes.values():
                forwarded_task_packets.extend(
                    node.sim_time_slice(time_slice, curr_time)
                )
            # Route heartbeat and forwarded task packets
            MalcolmNode.route_packets(forwarded_task_packets)
            # Collect metrics
            metrics = self.get_metrics()
            if not self.metrics:
                for metric_name in metrics:
                    self.metrics[metric_name] = {}
                    for node_name in MalcolmNode.all_nodes:
                        self.metrics[metric_name][node_name] = []
            for metric_name,values in metrics.items():
                for node_name,value in values.items():
                    self.metrics[metric_name][node_name].append(value)
            curr_time += time_slice
            self.logger.info("End of time slice\n\n")
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
                CentralLoadBalancer.distribute(new_tasks)
            )
            # Signal nodes to start time_slice
            MalcolmNode.start_time_slice.set()
            # Wait for nodes finish time_slice
            MalcolmNode.barrier.wait(TIMEOUT)
            # Clear start event while nodes are routing packets
            MalcolmNode.start_time_slice.clear()
            # TODO print interesting stuff
            #     (do not access MalcolmNode incoming_tasks or other_heartbeats)
            # Wait for all nodes again
            MalcolmNode.barrier.wait(TIMEOUT)
        # Wait for all threads
        self.logger.info("")
        for thread in threads:
            print(f"Waiting for {thread.getName()}", end="\r")
            thread.join()
        print("All threads terminated"+" "*64)
        self.logger.info("Simulation completed")


    def plot_all(self) -> None:
        """Plot the metrics collected by the simulation"""
        for metric_name, metric in self.metrics.items():
            plt.figure(figsize=(10, 5))
            for node_name, values in metric.items():
                plt.plot(values, label=node_name)
            plt.title(metric_name)
            plt.xlabel("Time")
            plt.ylabel(metric_name)
            plt.legend()
            plt.grid(True)
            plt.savefig(f"{metric_name}.png")
            plt.close()



    @classmethod
    def test_schedular(cls) -> None:
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
