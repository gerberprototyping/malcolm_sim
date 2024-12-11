"""Contains malcolm_sim.PolicyOptimizer"""

from __future__ import annotations

import logging
import numpy as np

from malcolm_sim.load_manager import LoadManager

# from .malcolm_node import MalcolmNode


class PolicyOptimizer:
    """Tracks heartbeats from other Nodes sends adjustments to the Load Manager"""

    def __init__(self, name:(str|int), node) -> None:
        self.name = str(name)
        self.node = node
        self.logger = logging.getLogger(f"malcolm_sim.MalcolmNode.PolicyOptimizer:{self.name}")

    def utility(self, current_load, other_loads):
        """Compute the reward as the negative of the load imbalance."""
        sum = 0 
        for load in other_loads:
            sum += load
        avg_load = sum/len(other_loads)
        # with more information from the node availability in heart beat load will change
        # There will also be an additional cost with cost
        # imbalance = sum((current_load - load)**2 for load in other_loads) - additional cost of action
        imbalance = (current_load - avg_load)
        return -imbalance

    def sim_time_slice(self, time_slice:float, load_manager:LoadManager) -> None:
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

        Maybe since their algorithm involves some sort of machine learning I can just use the fact
        that we know what the time it would take of the nodes to complete with the information
        of cores and effiency would take.
        """
        if 0 < time_slice:
            if self.node.other_heartbeats:
                load_manager.src = self.node.name
                load = len(self.node.schedular.queue)/self.node.schedular.expected_performance()
                self.logger.debug(f"My load: {load}")
                other_loads = []
                other_nodes = {}
                for key, value in self.node.other_heartbeats.items():
                    other_loads.append(value.queue_size/value.expected_performance)
                    other_nodes[key] = value.queue_size
                for key in self.node.other_heartbeats.keys():
                    load_manager.possible_destinations.append(key)
                reward = self.utility(load, [load]+other_loads)
                self.logger.debug(f"Other Nodes: {other_nodes}")
                self.logger.debug(f"Reward: {reward}")
                #if utility function changes inequality will need to change (which may be tricky)
                #will also need to change if we decide we want to steal tasks
                if reward < 0:
                    self.logger.debug(f"Increase forward policy: accept {load_manager.accept}, forward: {load_manager.forward}")
                    load_manager.accept = max(0, load_manager.accept - round(1/(1+len(other_nodes))**2, 2))
                    load_manager.forward = min(1, load_manager.forward + round(1/(1+len(other_nodes))**2, 2))
                elif reward > 0:
                    self.logger.debug(f"Increase accept policy: accept {load_manager.accept}, forward: {load_manager.forward}")
                    load_manager.accept = min(1, load_manager.accept + round(1/(1+len(other_nodes))**2, 2))
                    load_manager.forward = max(0, load_manager.forward - round(1/(1+len(other_nodes))**2, 2))
                else:
                    self.logger.debug(f"Keep policy: accept {load_manager.accept}, forward: {load_manager.forward}")

            else:
                self.logger.debug("no heart beats")
