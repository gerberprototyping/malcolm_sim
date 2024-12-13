# Introduction


# Previous Work


# Methodology

The system is simulated as a set of heterogenous Malcolm Nodes connected using
simulated network links. A central loadbalancer evenly distributes incoming tasks
to the Malcolm Nodes. The core component of the simulation is a Distributed
Load-Balancing game (DLB) in the Load Manager of each Malcolm Node.

\vspace{1em}

![Malcolm Node Architecture](./figs/malcolm_node.drawio.png) \
**Figure 1.** Malcolm node architecture

## Malcolm Node: Network Subsystem

Each Malcolm Node contains a Network Subsystem responsible for receiving task
packets from the Central Loadbalancer and sending and receiving task packets and
heartbeat packets to/from other Malcolm Nodes. Bandwidth limiting, packet
overhead, and latency are controlled by the sender. Receivers have no bandwidth
limit, overhead, or latency.

## Malcolm Node: Load Manager

## Malcolm Node: Policy Optimizer

## Malcolm Node: Intra-node Schedular

The intra-node schedular is responsible for scheduling and executing tasks within
the Malcolm Node. Tasks are received from the

These tasks are queued and evaluated by a set of Execution
Units

## Task Generation

The Random Task Generator is responsible for generating random tasks for the
simulation at a randomly changing rate.

## Heartbeat


# Results

**Table 1.** Simulation Statistics

|               | CPU Util  | CPU Queue | Latency   |
|---------------|-----------|-----------|-----------|
| Node 0 Max    | 100 %     | 24        | 31        |
| Node 1 Max    | 100 %     | $~$ 7     | 26        |
| Node 0 Min    | $~~$ 0 %  | $~$ 0     | $~~$ -    |
| Node 1 Min    | $~~$ 0 %  | $~$ 0     | $~~$ -    |
| Node 0 Avg.   | $~$ 92.4 %| $~$ 2.89  | $~$ 7.85  |
| Node 1 Avg.   | $~$ 86.5 %| $~$ 1.00  | $~$ 4.50  |

![CPU Utilization](./figs/2node_CPU_Util.png) \
**Figure 2.** CPU utilization

![CPU Queue](./figs/2node_CPU_Queue.png) \
**Figure 3.** CPU task queue size

![Task Latency](./figs/2node_Latency.png) \
**Figure 4.** Task latency



# Conclusion
