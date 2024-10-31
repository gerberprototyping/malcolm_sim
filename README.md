# Malcolm Simulation
A simulation for the research paper [Malcolm: Multi-agent Learning for Cooperative Load Management at Rack Scale](https://dl.acm.org/doi/10.1145/3570611).
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

| Parameters    | Description |
|---------------|-------------|
| Bandwidth     | Total network bandwidth in Bits/s (int)
| Overhead      | Packet overhead in bytes (int)
| Latency       | Network latency in milliseconds (float)

### Load Manager

The Load Manager and the DLB game is the core component of this simulation.

#### Distributed Load-Balancing Game (DLB)

TODO

### Policy Optimizer

The Policy Optimizer is responsible for receiving incoming heartbeats from the
Network Subsystem as well as sending its own heartbeat. Its primary role is to
analyze the up-to-date load of the current node and out-of-date load of other
nodes and send policy adjustments to the Load Manager and DLB game. Additionally,
an integer scalar is sent to the Central Loadbalancer to adjust the distribution
of incoming tasks (default is 8).

### Intra-node Schedular

This subsystem is responsible for scheduling and executing tasks within the
Malcolm Node. These tasks are queued and evaluated by a set of Execution Units

| Parameters    | Description |
|---------------|-------------|
| Cores         | Core count of this Malcolm Node (int)
| Performance   | Performance multiplier for cores in this Malcolm Node (float)
| Overhead      | Overhead in milliseconds for task execution (float)

## Central Loadbalancer

Tasks are distributed among the Malcolm nodes based on their adjustable
distribution scalar (default 8).

TODO distribution algorithm

## Tasks

Tasks each have various parameters such as CPU busy `Runtime`, CPU Idle `IOTime`,
and packet size `Payload`. The only subsystem that should observe these
parameters is the Execution Unit of the Intra-node Schedular. All other
subsystems should treat them as black-box and of equal weight/difficulty.

| Parameters    | Description |
|---------------|-------------|
| Runtime       | Active CPU time in millisecond (float)
| IOTime        | IO wait time in millisecond (float)
| Payload       | Size in bytes of payload

## Heartbeat
