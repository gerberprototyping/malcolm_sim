"""This file contains malcolm_sim.TaskGen and related dataclasses"""
# pylint: disable=attribute-defined-outside-init

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable, Dict, List

from numpy import random

from .task import Task
from .function_call import FunctionCall


@dataclass
class GaussianParams: # pylint: disable=missing-class-docstring
    center:float
    scale:float
    def as_kwargs(self) -> Dict[str, float]:
        """Returns this instance as a dict to be used as kwargs"""
        return {"loc": self.center, "scale":self.scale}


class TaskGen:
    """Random Task Generator"""

    logger = logging.getLogger("malcolm_sim.TaskGen")


    @classmethod
    def from_config(cls, config:dict) -> TaskGen:
        """Create a Task Generator from config dict. Assumes schema is validated"""
        kwargs = {
            "rate_func": None,
            "runtime_func": None,
            "io_time_func": None,
            "payload_func": None
        }
        for key,params in config.items():
            kw = f"{key}_func"
            _type = params.pop("type")
            if _type in ["const", "constant"]:
                kwargs[kw] = FunctionCall(lambda x,size=1: [x]*size, params["value"])
            elif "gaussian" == _type:
                kwargs[kw] = FunctionCall(random.normal, **params)
            else:
                raise ValueError(f"Task parameter type '{_type}' is invalid")
        return cls(**kwargs)


    @classmethod
    def new_gaussian(cls,
        rate_params:GaussianParams,
        runtime_params:GaussianParams,
        io_time_params:GaussianParams,
        payload_params:GaussianParams
    ) -> TaskGen:
        """Create a Task Generator from gaussian parameters"""
        return cls(
            FunctionCall(random.normal, **rate_params.as_kwargs()),
            FunctionCall(random.normal, **runtime_params.as_kwargs()),
            FunctionCall(random.normal, **io_time_params.as_kwargs()),
            FunctionCall(random.normal, **payload_params.as_kwargs())
        )


    def __init__(self,
        rate_func:FunctionCall,
        runtime_func:FunctionCall,
        io_time_func:FunctionCall,
        payload_func:FunctionCall,
    ) -> None:
        self.id_count = 0
        self.rate_func = rate_func
        self.runtime_func = runtime_func
        self.io_time_func = io_time_func
        self.payload_func = payload_func


    def gen_time_slice(self, time_slice:float, curr_time:float) -> List[Task]:
        """Generate all tasks for a time slice"""
        rate = self.rate_func()[0]
        num_tasks = int(rate*time_slice*1000)
        task_args:List[List[(float|int)]] = (
            self.runtime_func(size=num_tasks),
            self.io_time_func(size=num_tasks),
            self.payload_func(size=num_tasks),
        )
        tasks = []
        for args in zip(*task_args):
            attrs = {"gen_time": curr_time}     # must be inside loop
            tasks.append(Task(f"#{self.id_count}", *args, attrs=attrs))
            self.id_count += 1
        return tasks
