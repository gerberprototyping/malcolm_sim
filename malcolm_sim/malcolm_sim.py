"""Contains the primary class for the malcolm_sim module"""

import logging

from .schedular import Schedular
from .task import Task
from .log import get_main_logger


class MalcolmSim:
    """Primary class of the malcolm_sim module. Allows simulating a Malcolm Cluster"""

    logger:logging.Logger = get_main_logger("malcolm_sim", "malcolm_sim.log")

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
            perf=1,
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
