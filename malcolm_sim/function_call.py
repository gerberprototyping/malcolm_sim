"""Contains the FunctionCall class"""

from __future__ import annotations


class FunctionCall:
    """This class takes a function and its arguments to be called elsewhere"""

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, **kwargs) -> any:
        return self.func(*self.args, **self.kwargs, **kwargs)
