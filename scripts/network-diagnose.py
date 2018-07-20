## Generating Accessibility Vars
# 
# Paul Waddell, UrbanSim, July 2018
#

import os
os.chdir('../')
import numpy as np, pandas as pd 
import orca
from scripts import datasources
from scripts import models

orca.run(["initialize_network_walk"])
orca.run(["network_aggregations_walk_test"])
