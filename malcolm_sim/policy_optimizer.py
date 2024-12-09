"""Contains malcolm_sim.PolicyOptimizer"""

from __future__ import annotations

import logging

# from .malcolm_node import MalcolmNode


class PolicyOptimizer:
    """Tracks heartbeats from other Nodes sends adjustments to the Load Manager"""

    def __init__(self, name:(str|int), node) -> None:
        self.name = str(name)
        self.node = node
        self.logger = logging.getLogger(f"malcolm_sim.MalcolmNode.LoadManager:{self.name}")

    def sim_time_slice(self, time_slice:float) -> None:
        """
        Simulate Policy Optimizer for time_slice milliseconds.
        Makes adjustments to node.load_manager based on heartbeats of other nodes

        Input: 
        - α: Critic learning rate
        - β: Actor learning rate

        Initialize: 
        - θ_i and w_i for each agent i ∈ N (initialization of critic and actor parameters)

        Repeat (Forever loop):
            For each agent i ∈ N:
                - Take action based on the policy π_w_i(x_r)
                - Observe the action a_r and the new state x_r+1

            For each agent i ∈ N (Training step):
                - Compute the global utility u_r (based on Equation 1)
                - Calculate the difference δ_r:
                    δ_r = u_r + γ * V_θ_i(x_r+1) - V_θ_i(x_r)
                
                - Update the critic parameters θ_i:
                    θ_i ← θ_i + α * δ_r * ∇_θ_i V_θ_i
                
                - Update the actor parameters w_i:
                    w_i ← w_i + β * δ_r * ∇_w_i log(π_w_i(a_r, x_r))

            For each agent i ∈ N (Consensus step):
                - If r % P == 0 (periodic synchronization):
                    - Average the critic parameters θ_i across all agents:
                        θ_i ← (1 / N) * Σ (θ_j for j ∈ N)

        """
        curr_time:float = 0
        while curr_time < time_slice:
            for key, value in self.node.all_nodes.items():
                print(key)
                print(value.get_heartbeat_)
            curr_time += 1

        raise NotImplementedError()
