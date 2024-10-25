# Malcolm Simulation
A simulation for the research paper [Malcolm: Multi-agent Learning for Cooperative Load Management at Rack Scale](https://dl.acm.org/doi/10.1145/3570611).
This group is unaffiliated with the original researchers.

The system is simulated as a set of heterogenous Malcolm nodes is are connected
simulated network links. A central loadbalancer randomly and semi-evenly
distributes incoming tasks to the Malcolm nodes. The core component of the
simulation is a Distributed Load-Balancing game (DLB) in the Load Manager of
each Malcolm node.

## Malcolm Node

Each Malcolm node consists of four major subsystems:

- Network Subsystem
- Load Manager
- Policy Optimizer
- Intra-node Schedular

### Network Subsystem

### Load Manager

#### Distributed Load-Balancing Game (DLB)

### Policy Optimizer

### Intra-node Schedular

## Central Loadbalancer

Tasks are distributed randomly and semi-evenly distributed among the Malcolm
nodes.

## Tasks

| Parameters |
|------------|
| Runtime
| IOTime
