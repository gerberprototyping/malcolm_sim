# Malcolm Simulation

A simulation for the research paper
[Malcolm: Multi-agent Learning for Cooperative Load Management at Rack Scale](https://dl.acm.org/doi/10.1145/3570611).
This group is unaffiliated with the original researchers.

The system is simulated as a set of heterogenous Malcolm Nodes is are connected
simulated network links. A central loadbalancer distributes incoming tasks to
the Malcolm Nodes. The core component of the simulation is a Distributed
Load-Balancing game (DLB) in the Load Manager of each Malcolm Node.

## Malcolm Node

Malcolm Nodes in the system may be heterogenous, but cores within a Malcolm Node
are homogeneous.

Each Malcolm Node consists of four major subsystems:

- Network Subsystem
- Load Manager
- Policy Optimizer
- Intra-node Schedular

### Network Subsystem

Each Malcolm Node contains a Network Subsystem responsible for receiving task
packets from the Central Loadbalancer and sending and receiving task packets and
heartbeat packets to/from other Malcolm Nodes. Bandwidth limiting, packet
overhead, and latency are controlled by the sender. Receivers have no bandwidth
limit, overhead, or latency.

| Parameters | Description                             |
| ---------- | --------------------------------------- |
| Bandwidth  | Total network bandwidth in Bits/s (int) |
| Overhead   | Packet overhead in bytes (int)          |
| Latency    | Network latency in milliseconds (float) |

### Load Manager

The Load Manager and the DLB game is the core component of this simulation.

### Distributed Load-Balancing Game (DLB)

The goal of the DBL game is to balance the tasks across nodes, which process
them at various rates. Each node has a load manager which decides whether to
keep a task or migrate it to another node and even steal a task. The game is a
Markov game wich generalizes both markov decision processes and repeated games.
N heterogeneous nodes are represented by N agents. The game is divided into
rounds:

- node 𝑖 receives a new task with probability 𝑝𝑖 and completes a task with
  probability 𝑞𝑖

| Parameters | Description                                              |
| ---------- | -------------------------------------------------------- |
| States     | Evolves over time as agents take scheduling actions      |
| Actions    | Agents can accept or steal a task from another node      |
| Strategy   | provides a description of how an agent plays the game    |
| Utility    | captures cost of load imbalance, migrations and stealing |

#### States and Actions

The load on each node represents its current state. The state of the game
evolves over time as agents take scheduling actions.

- The load on node 𝑖 at round 𝑟 is denoted by 𝑥[𝑖][𝑟] . The state of the game at
  round 𝑟 is 𝑥[𝑟] = (𝑥[1][𝑟] ,...,𝑥[𝑁][𝑟]).
- We denote the set of scheduling actions taken by agent 𝑖 at round 𝑟 by 𝑎[𝑖][𝑟]
  .
  - We use 𝑎[𝑟] = (𝑎[1][𝑟] ,...,𝑎[𝑁][𝑟]) to aggregate all actions taken by all
    nodes at round 𝑟.

#### Strategies

A strategy describes the way an agent plays the game. The algorithm uses a
stationary strategy, where it only depends on the final state of each history,
making decisions based on the current system load

- Let h[𝑟] = (𝑥0,𝑎0,𝑥1,𝑎1,...,𝑥𝑟 )denote the history of the game at round 𝑟.

#### Utility

The utility function measures the cost of load imbalance across nodes and
includes the costs of migration and work stealing requests. It uses a linear
function C to calculate penalties for migration and work-stealing.

- Let 𝜋[𝑖] denote the strategy of agent 𝑖, and let 𝜋[−𝑖] =
  (𝜋1,...,𝜋𝑖−1,𝜋𝑖+1,...,𝜋𝑁 ) represent the strategy of all agents other than i.

### Policy Optimizer

The Policy Optimizer is responsible for receiving incoming heartbeats from the
Network Subsystem as well as sending its own heartbeat. Its primary role is to
analyze the up-to-date load of the current node and out-of-date load of other
nodes and send policy adjustments to the Load Manager and DLB game.

### Intra-node Schedular

This subsystem is responsible for scheduling and executing tasks within the
Malcolm Node. These tasks are queued and evaluated by a set of Execution Units

| Parameters       | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| Cores            | Number of cores in this Malcolm Node (int)                         |
| Core Performance | Performance multiplier for cores in this Malcolm Node (float)      |
| IO Cores         | Number of concurrent IO tasks supported in this Malcolm Node (int) |
| IO Performance   | Performance multiplier for IO in this Malcolm Node (float)         |
| Overhead         | Overhead in milliseconds for task execution (float)                |

## Central Loadbalancer

Tasks are distributed among Malcolm nodes via round-robin.

## Tasks

Tasks each have various parameters such as CPU busy `Runtime`, CPU Idle
`IOTime`, and packet size `Payload`. The only subsystem that should observe
these parameters is the Execution Unit of the Intra-node Schedular. All other
subsystems should treat them as black-box and of equal weight/difficulty.

| Parameters | Description                            |
| ---------- | -------------------------------------- |
| Runtime    | Active CPU time in millisecond (float) |
| IOTime     | IO wait time in millisecond (float)    |
| Payload    | Size in bytes of payload               |

## Heartbeat

TODO

## Random Task Generator

The Random Task Generator is responsible for generated random tasks for the
simulation at a randomly changing rate.

| Parameters | Description                                                           |
| ---------- | --------------------------------------------------------------------- |
| Rate       | A random distribution function to control the rate of generated tasks |
| Runtime    |
| IOTime     |
| Payload    |
