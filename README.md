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
rounds and each round each node i can receive a new task with probability q_i or
complete a task with probability q_i.

#### States and Actions

The load on each node represents its current state. the load on node i at round
r is denoted by x_i,r and at round r the state is x_r = (x_1r, ... , x_Nr). The
state of the game evolves over time as agents take scheduling actions. A
scheduling action taken by agent i at round r is denoted as a_ir and all
agrregated represented as a_r (a_1r, ... ,a_Nr).

#### Strategies

A strategy, 𝜋, describes the way an agent plays the game. Let h_r =
(x_0,a_0,x_1,a_1,...,x_r )denote the history of the game at round 𝑟. The
algorithm uses a stationary strategy, where it only depends on the final state
of each history, making decisions based on the current system load

#### Utility

The utility function measures the cost of load imbalance across nodes and
includes the costs of migration and work stealing requests represented as: 𝑢(𝑥*𝑟
,𝑎*𝑟 )=−∑︁*i,j(𝑥*𝑖𝑟−𝑥*𝑗, )^2−𝐶(𝑎). It uses a linear function C to calculate
penalties for migration and work-stealing. Let 𝜋*𝑖 denote the strategy of agent
𝑖, and let 𝜋*−𝑖 = (𝜋_1,...,𝜋\_(𝑖−1),𝜋\_(𝑖+1),...,𝜋*𝑁 )represent the strategy of
all agents other than 𝑖. The value function represents the long-term value of a
state 𝑥 for each agent 𝑖under strategy 𝜋 = (𝜋*𝑖 ,𝜋*−𝑖 ), and it is defined as:
𝑉^𝑖_𝑥(𝜋)= E[∑︁ 𝛿^𝑟 𝑢(𝑥\_𝑟 ,𝑎\_𝑟 )|𝑎\_𝑟 ∼𝜋,𝑥_0 = 𝑥 ]. This function captures the
expected payoff in state 𝑥 plus the expected discounted sum of future payoffs.

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
