"""The malcolm_sim.Task class"""

from __future__ import annotations

import inspect
from typing import Dict


class Task:
    """Modules a task to be executed in a Malcolm Cluster"""

    def __init__(self,
                 name:(str|int),
                 runtime:float,
                 io_time:float,
                 payload:int,
                 attrs:Dict[str,any]=None,
    ) -> None:
        self.name = str(name)
        self.runtime:float = runtime        # total CPU runtime of
        self.io_time:float = io_time        # total IO time of
        self.payload:int = payload          # size of payload in bytes
        self.progress:float = 0             # current executed CPU runtime
        self.io_progress:float = 0          # current executed IO time
        if attrs is None:
            attrs = {}
        self.attrs:Dict[str,dict] = attrs   # dictionary of attributes

    def cpu_remaining(self) -> float:
        """Returns the remaining amount of CPU runtime"""
        return self.runtime - self.progress

    def io_remaining(self) -> float:
        """Returns the remaining amount of IO time"""
        return self.io_time - self.io_progress

    def is_cpu_done(self) -> bool:
        """Returns True if the CPU portion of this task is complete"""
        return self.progress >= self.runtime

    def is_io_done(self) -> bool:
        """Returns True if the IO portion of this task is complete"""
        return self.io_progress >= self.io_time

    def is_done(self) -> bool:
        """Returns true if the task has finished execution"""
        return self.is_cpu_done() and self.is_io_done()

    def get_attr(self, key:str) -> any:
        """Get an attribute from this task, returns None of not found"""
        return self.attrs[key] if key in self.attrs else None

    def sim_cpu(self, delta_t:float) -> bool:
        """
        Simulate delta_t milliseconds of CPU time.
        Returns True if the CPU portion of this task completes
        """
        if delta_t < self.cpu_remaining():
            self.progress += delta_t
            return False
        else:
            self.progress = self.runtime
            return True

    def sim_io(self, delta_t:float) -> bool:
        """
        Simulate delta_t milliseconds of IO time.
        Returns True if the IO portion of this task completes
        """
        if delta_t < self.io_remaining():
            self.io_progress += delta_t
            return False
        else:
            self.progress = self.io_time
            return True


    def __str__(self) -> str:
        rval =  f"Task '{self.name}':\n"
        rval += f"    CPU time: {self.progress:g}/{self.runtime:g} ms\n"
        rval += f"    IO time:  {self.io_progress:g}/{self.io_time:g} ms\n"
        rval += f"    Payload:  {self.payload} bytes"
        if self.attrs:
            rval += "\n    Attrs:"
            for key,val in self.attrs.items():
                if inspect.isclass(val):
                    val = type(val).__name__ + " object"
                rval += f"\n    - '{key}': {val}"
        return rval

    def short_str(self) -> str:
        """Return a shortened version of the string representation of this Task"""
        rval =  f"Task '{self.name}': CPU={self.runtime:g}; IO={self.io_time:g}"
        rval += f"; Payload={self.payload}"
        if main_task := self.get_attr("overhead"):
            rval += f"; main_task='{main_task.name}'"
        return rval
