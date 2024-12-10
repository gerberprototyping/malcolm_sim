"""This file contains the intra-node Schedular class for the malcolm_sim module"""

from __future__ import annotations

import logging
from typing import Iterable, List

from .task import Task
from .thread_safe_list import ThreadSafeList


CONCURRENCY_TIMEOUT = 1


class Schedular:
    """Intra-node Schedular of a Malcolm Node"""

    class ExecUnit:
        """Models a CPU core or IO thread"""

        def __init__(self) -> None:
            self.task:Task = None

        def is_busy(self) -> bool:
            """Returns true if the ExecUnit is currently executing a task"""
            return self.task is not None

        def is_idle(self) -> bool:
            """Returns true if the ExecUnit is not currently executing a task"""
            return self.task is None


    def __init__(self,
                 name:(str|int),
                 core_count:int,
                 core_perf:float,
                 io_count:int,
                 io_perf:float,
                 overhead:float
    ) -> None:
        self.name = str(name)
        self.core_count:int = core_count
        self.core_perf:float = core_perf
        self.io_count:int = io_count
        self.io_perf:float = io_perf
        self.overhead:float = overhead
        self.completed:int = 0
        self.logger = logging.getLogger(f"malcolm_sim.MalcolmNode.Schedular:{self.name}")

        # Queue to hold tasks pending CPU execution
        self.queue:ThreadSafeList[Task] = ThreadSafeList()
        # Queue to hold tasks pending IO execution
        self.io_queue:List[Task] = []
        # List of tasks each core is working on
        self.cores:List[Schedular.ExecUnit] \
            = [Schedular.ExecUnit() for _ in range(self.core_count)]
        # List of tasks each IO is working on
        self.ios:List[Schedular.ExecUnit] \
            = [Schedular.ExecUnit() for _ in range(self.io_count)]
        # Track per core utilization (0-1)
        self.core_utilization:float = 0
        # Track per IO utilization (0-1)
        self.io_utilization:float = 0


    def core_availability(self) -> float:
        """Return total unutilized CPU (thread-safe)"""
        avail = (1-self.core_utilization) * self.core_perf
        return avail


    def io_availability(self) -> float:
        """Return total unutilized IO (thread-safe)"""
        avail = (1-self.io_utilization) * self.io_perf
        return avail


    def availability(self) -> float:
        """Return the system availability as the min of CPU and IO availability (thread-safe)"""
        return min(self.core_availability(), self.io_availability())


    def add_tasks(self, tasks:Iterable) -> None:
        """Add tasks to this scheduler's queue (thread-safe)"""
        self.queue.extend(tasks)


    def sim_time_slice(self, time_slice:float) -> List[Task]:
        """
        Simulate execution for time_slice milliseconds.
        Returns a list of tasks that have completed execution
        (NOT thread-safe)
        """
        curr_time:float = 0    # current time in this time slice
        completed:List[Task] = []
        core_busy_time:List[float] = [0]*self.core_count
        io_busy_time:List[float] = [0]*self.io_count
        prev_delta_t = -1
        self.logger.info("Simulating time slice +%g ms", time_slice)
        self.logger.debug("Task queue: size=%d", len(self.queue))
        if self.logger.isEnabledFor(logging.TRACE):
            for task in self.queue.as_list():
                print("    "+str(task))
        # Simulation loop within time slice, each iteration is a single event
        while curr_time < time_slice:
            self.logger.debug("curr_time = +%g", curr_time)
            delta_t:float = -1  # time until next event
            # Assign new tasks to idle cores
            for i,core in enumerate(self.cores):
                if core.is_idle() and self.queue:
                    task = self.queue.pop()
                    # Add overhead before running task
                    core.task = self._overhead_task(task)
                    self.logger.debug(
                        "Scheduling%s task %s on core %d",
                        " overhead for" if self.overhead>0 else "", task.name, i
                    )
                # idle state may have changed, check again
                if core.is_busy():
                    this_delta_t = core.task.cpu_remaining()
                    self.logger.trace(
                        "Task %s on core %d has %g ms CPU time remaining",
                        core.task.name, i, this_delta_t
                    )
                    if delta_t >= 0:
                        if this_delta_t < delta_t:
                            # events = [core]
                            delta_t = this_delta_t
                        # elif this_delta_t == delta_t:
                        #     events.append(core)
                    else:
                        # events = [core]
                        delta_t = this_delta_t
                else:
                    self.logger.trace("Core %d is IDLE", i)
            # Assign new tasks to idle IOs
            for i,io in enumerate(self.ios):
                if io.is_idle() and self.io_queue:
                    # No overhead for IO
                    io.task = self.io_queue.pop()
                    self.logger.debug("Scheduling task %s on IO %d",io.task.name, i)
                # idle state may have changed
                if io.is_busy():
                    this_delta_t = io.task.io_remaining()
                    self.logger.trace(
                        "Task %s on IO %d has %g ms IO time remaining",
                        io.task.name, i, this_delta_t
                    )
                    if delta_t >= 0:
                        if this_delta_t < delta_t:
                            # events = [io]
                            delta_t = this_delta_t
                        # elif this_delta_t == delta_t:
                        #     events.append(io)
                    else:
                        # events = [io]
                        delta_t = this_delta_t
                else:
                    self.logger.trace(": IO %d is IDLE", i)
            self.logger.debug("Current state\n%s", self.state_str())
            # Done if all cores/IOs are idle
            if delta_t < 0:
                break
            elif prev_delta_t == 0:
                self.logger.critical(
                    "Schedular:%s : Caught in infinite loop!\nDumping state\n%s",
                    self.name, self.state_str()
                )
                raise RuntimeError(f"Schedular:{self.name} : Caught in infinite loop!")
            # bound delta t within time_slice
            delta_t = min(delta_t, time_slice-curr_time)
            self.logger.debug("delta_t = %g", delta_t)
            # Simulate delta t milliseconds for each core
            for i,core in enumerate(self.cores):
                busy = core.is_busy()
                if busy:
                    core_busy_time[i] += delta_t
                if busy and core.task.sim_cpu(delta_t):
                    # Task finished CPU portion
                    if core.task.get_attr("overhead"):
                        # finished overhead, schedular main_task
                        self.logger.trace(
                            "Schedular:%s : Overhead task %s completed on core %d",
                            self.name, core.task.name, i
                        )
                        core.task = core.task.get_attr("main_task")
                    else:
                        if core.task.io_time > 0:
                            # Schedule IO
                            self.io_queue.append(core.task)
                            self.logger.debug(
                                "Schedular:%s : CPU execution completed for task %s on core %d" \
                                +"; adding to IO queue",
                                self.name, core.task.name, i
                            )
                        else:
                            # task complete
                            completed.append(core.task)
                            self.logger.debug(
                                "Schedular:%s : Completed task %s on core %d",
                                self.name, core.task.name, i
                            )
                        core.task = None
            # Simulate delta t milliseconds for each IO
            for i,io in enumerate(self.ios):
                busy = io.is_busy()
                if busy:
                    io_busy_time[i] += delta_t
                if busy and io.task.sim_io(delta_t):
                    # Task complete
                    completed.append(io.task)
                    self.logger.debug(
                        "Schedular:%s : Completed task %s on IO %d",
                        self.name, io.task.name, i
                    )
                    io.task = None
            # Increment current time
            curr_time += delta_t
            prev_delta_t = delta_t
        self.logger.info("Time slice simulation complete")
        self.completed = len(completed)
        if completed:
            task_str = ""
            for task in completed:
                task_str += f"    - {task.name}\n"
            task_str = task_str[0:-1]
            self.logger.info(
                "Schedular:%s : Completed %d task(s)\n%s",
                self.name, len(completed), task_str
            )
        else:
            self.logger.debug("No tasks completed")
        # Update utilization and return completed tasks
        self.core_utilization = sum(core_busy_time) / self.core_count / time_slice
        self.logger.debug(f"Core utilization: {self.core_utilization}")
        self.io_utilization = sum(io_busy_time) / self.io_count / time_slice
        self.logger.debug(f"IO utilization: {self.io_utilization}")
        return completed


    def _overhead_task(self, main_task:Task) -> Task:
        """Create a schedular overhead wrapper task (thread-safe)"""
        if self.overhead <= 0:
            return main_task
        attrs = {
            "overhead": True,
            "main_task": main_task,
        }
        return Task(f"overhead.{main_task.name}", self.overhead, 0, -1, attrs=attrs)


    def __str__(self) -> str:
        """String summary of this Schedular (thread-safe)"""
        rval =  f"Schedular '{self.name}':\n"
        rval += f"    cores:     {self.core_count}"
        if self.core_perf != 1:
            rval += f"  (x{self.core_perf:g})"
        rval += f"\n    ios:       {self.io_count}"
        if self.io_perf != 1:
            rval += f"  (x{self.io_perf:g})"
        rval += f"\n    overhead:  {self.overhead} ms\n"
        rval += f"    CPU tasks: {len(self.queue)}\n"
        rval += f"    IO tasks:  {len(self.io_queue)}"
        return rval


    def state_str(self) -> str:
        """Details about the current state of each core and IO (thread-safe)"""
        rval = f"Schedular:{self.name}\n"
        for i,core in enumerate(self.cores):
            rval += f"    Core {i}: "
            if core.is_busy():
                rval += f"Task '{core.task.name}' {core.task.progress}/{core.task.runtime}\n"
            else:
                rval += "IDLE\n"
        prev = "busy"
        for i,io in enumerate(self.ios):
            if io.is_busy():
                s = f"    IO {i}: Task '{io.task.name}' {io.task.io_progress}/{io.task.io_time}\n"
            else:
                s = f"    IO {i}: IDLE\n"
            if "busy" == prev:
                rval += s
                if io.is_busy():
                    prev = "busy"
                else:
                    prev = "idle"
            elif "idle" == prev:
                if io.is_busy():
                    rval += s
                    prev = "busy"
                else:
                    rval += "    ...\n"
                    prev = "..."
            elif "..." == prev:
                if io.is_busy() or i == self.io_count-1:
                    rval += s
                    prev = "busy"
        return rval
