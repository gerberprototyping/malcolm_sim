#!/usr/bin/env python3

import logging
from malcolm_sim import MalcolmSim

# MalcolmSim.test_schedular()

sim = MalcolmSim.from_json_yaml("conf.yaml")
# sim.logger.setLevel(logging.DEBUG)
# sim.logger.setLevel(logging.TRACE)
sim.logger.setLevel(logging.WARNING)

sim.run(1, 5000)
sim.plot_all()
