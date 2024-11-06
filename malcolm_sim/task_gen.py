"""This file contains malcolm_sim.TaskGen and related dataclasses"""
# pylint: disable=attribute-defined-outside-init

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, List

from numpy import random

from .task import Task


@dataclass
class GaussianParams: # pylint: disable=missing-class-docstring
    center:float
    scale:float


class TaskGen:
    """Random Task Generator"""

    logger = logging.getLogger("malcolm_sim.TaskGen")

    def __init__(self) -> None:
        self.id_count = 0

    def config_gaussian(self,
        rate_func:Callable,
        runtime:GaussianParams,
        io_time:GaussianParams,
        payload:GaussianParams
    ):
        """Configure this instance to use gaussian distributions"""
        self.func = TaskGen._gen_gaussian
        self.rate_func = rate_func
        self.runtime = runtime
        self.io_time = io_time
        self.payload = payload

    def gen_time_slice(self, time_slice:float) -> List[Task]:
        """Generate all tasks for a time slice"""
        self.func(self, time_slice)

    def _gen_gaussian(self, time_slice:float) -> Task:
        rate = self.rate_func()
        num_tasks = int(rate*time_slice*1000)
        task_args = (
            random.normal(loc=self.runtime.center, scale=self.runtime.scale, size=num_tasks),
            random.normal(loc=self.io_time.center, scale=self.io_time.scale, size=num_tasks),
            random.normal(loc=self.payload.center, scale=self.payload.scale, size=num_tasks),
        )
        tasks = []
        for args in zip(*task_args):
            tasks.append(Task(f"#{self.id_count}", *args))
            self.id_count += 1
        return tasks
