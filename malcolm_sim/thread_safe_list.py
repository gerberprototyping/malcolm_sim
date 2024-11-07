"""This file contains an simple implementation of a thread-safe list"""

from threading import Lock, Condition
from typing import Generic, Iterable, List, SupportsIndex, TypeVar

TIMEOUT = 10
TIMEOUT_MSG = "Dead-lock detected"


T = TypeVar("T")
class ThreadSafeList(Generic[T]):
    """A thread-safe list with automatic dead-lock detection based on timeouts"""

    def __init__(self):
        self.list:List[T] = []
        self.lock:Lock = Lock()
        self.condition:Condition = Condition(self.lock)

    def insert(self, index:SupportsIndex, item:T) -> None:
        """Insert object before index"""
        with self.condition:
            # if not self.condition.wait_for(lambda: True, TIMEOUT):
            #     raise TimeoutError(TIMEOUT_MSG)
            self.list.insert(index, item)
            self.condition.notify_all()

    def append(self, item:T) -> None:
        """Append object to the end of the list"""
        with self.condition:
            # if not self.condition.wait_for(lambda: True, TIMEOUT):
            #     raise TimeoutError(TIMEOUT_MSG)
            self.list.append(item)
            self.condition.notify_all()

    def extend(self, items:Iterable[T]) -> None:
        """Extend this list by appending elements the iterable"""
        with self.condition:
            # if not self.condition.wait_for(lambda: True, TIMEOUT):
            #     raise TimeoutError(TIMEOUT_MSG)
            self.list.extend(items)
            self.condition.notify_all()

    def get(self, index:SupportsIndex) -> T:
        """Get object at index from the list"""
        with self.condition:
            if not self.condition.wait_for(lambda: index < len(self.list), TIMEOUT):
                raise TimeoutError(TIMEOUT_MSG)
            return self.list[index]

    def remove(self, item:T) -> None:
        """Remove first occurrence of a value"""
        with self.condition:
            if not self.condition.wait_for(lambda: item in self.list, TIMEOUT):
                raise TimeoutError(TIMEOUT_MSG)
            self.list.remove(item)
            self.condition.notify_all()

    def push(self, item:T) -> None:
        """Append object to the end of the list"""
        with self.condition:
            # if not self.condition.wait_for(lambda: True, TIMEOUT):
            #     raise TimeoutError(TIMEOUT_MSG)
            self.list.insert(0, item)
            self.condition.notify_all()

    def push_all(self, items:Iterable[T]) -> None:
        """Extend this list by appending elements the iterable"""
        with self.condition:
            # if not self.condition.wait_for(lambda: True, TIMEOUT):
            #     raise TimeoutError(TIMEOUT_MSG)
            self.list.extend(items)
            self.condition.notify_all()

    def pop(self):
        """Remove and return object at the beginning of the list"""
        with self.condition:
            if not self.condition.wait_for(lambda: len(self.list), TIMEOUT):
                raise TimeoutError(TIMEOUT_MSG)
            rval:T = self.list.pop(0)
            self.condition.notify_all()
            return rval

    def __len__(self) -> int:
        with self.condition:
            # if not self.condition.wait_for(lambda: True, TIMEOUT):
            #     raise TimeoutError(TIMEOUT_MSG)
            return len(self.list)

    def __bool__(self) -> bool:
        with self.condition:
            # if not self.condition.wait_for(lambda: True, TIMEOUT):
            #     raise TimeoutError(TIMEOUT_MSG)
            return len(self.list) > 0

    def __repr__(self):
        with self.lock:
            return repr(self.list)
