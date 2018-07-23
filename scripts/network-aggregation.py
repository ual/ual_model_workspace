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


### Generate Node variables

#orca.run(["initialize_network_drive"])
#orca.run(["network_aggregations_drive"])

orca.run(["initialize_network_small"])
orca.run(["network_aggregations_small"])
orca.run(["initialize_network_walk"])
orca.run(["network_aggregations_walk"])

#nodesdrive = orca.get_table('nodesdrive').to_frame()

nodessmall = orca.get_table('nodessmall').to_frame()
nodeswalk = orca.get_table('nodeswalk').to_frame()

nodessmall_upper = nodessmall.quantile(.99)
nodessmall_c = nodessmall.clip_upper(nodessmall_upper, axis=1)
nodeswalk_upper = nodeswalk.quantile(.99)
nodeswalk_c = nodeswalk.clip_upper(nodeswalk_upper, axis=1)

nodeswalk_c['prop_children_500_walk'] = (nodeswalk_c['children_500_walk'] > 0).astype(int) / nodeswalk_c['hh_500_walk']
nodeswalk_c['prop_singles_500_walk'] = nodeswalk_c['singles_500_walk'] / nodeswalk_c['hh_500_walk']
nodeswalk_c['prop_elderly_500_walk'] = nodeswalk_c['elderly_hh_500_walk'] / nodeswalk_c['hh_500_walk']
nodeswalk_c['prop_black_500_walk'] = nodeswalk_c['pop_black_500_walk'] / nodeswalk_c['pop_500_walk']
nodeswalk_c['prop_white_500_walk'] = nodeswalk_c['pop_white_500_walk'] / nodeswalk_c['pop_500_walk']
nodeswalk_c['prop_asian_500_walk'] = nodeswalk_c['pop_asian_500_walk'] / nodeswalk_c['pop_500_walk']
nodeswalk_c['prop_hisp_500_walk'] = nodeswalk_c['pop_hisp_500_walk'] / nodeswalk_c['pop_500_walk']
nodeswalk_c['prop_rich_500_walk'] = nodeswalk_c['rich_500_walk'] / nodeswalk_c['pop_500_walk']
nodeswalk_c['prop_poor_500_walk'] = nodeswalk_c['poor_500_walk'] / nodeswalk_c['pop_500_walk']

nodeswalk_c['prop_children_1500_walk'] = (nodeswalk_c['children_1500_walk'] > 0).astype(int)/nodeswalk_c['hh_1500_walk']
nodeswalk_c['prop_singles_1500_walk'] = nodeswalk_c['singles_1500_walk'] / nodeswalk_c['hh_1500_walk']
nodeswalk_c['prop_elderly_1500_walk'] = nodeswalk_c['elderly_hh_1500_walk'] / nodeswalk_c['hh_1500_walk']
nodeswalk_c['prop_black_1500_walk'] = nodeswalk_c['pop_black_1500_walk'] / nodeswalk_c['pop_1500_walk']
nodeswalk_c['prop_white_1500_walk'] = nodeswalk_c['pop_white_1500_walk'] / nodeswalk_c['pop_1500_walk']
nodeswalk_c['prop_asian_1500_walk'] = nodeswalk_c['pop_asian_1500_walk'] / nodeswalk_c['pop_1500_walk']
nodeswalk_c['prop_hisp_1500_walk'] = nodeswalk_c['pop_hisp_1500_walk'] / nodeswalk_c['pop_1500_walk']
nodeswalk_c['prop_rich_1500_walk'] = nodeswalk_c['rich_1500_walk'] / nodeswalk_c['pop_1500_walk']
nodeswalk_c['prop_poor_1500_walk'] = nodeswalk_c['poor_1500_walk'] / nodeswalk_c['pop_1500_walk']

#nodesdrive.to_csv('data/nodesdrive_vars.csv')
parcel = orca.get_table('parcels').to_frame()
rentals = orca.get_table('rentals').to_frame()

nodessmall_c.to_csv('data/nodessmall_vars.csv')
nodeswalk_c.to_csv('data/nodeswalk_vars.csv')
parcels.to_csv('data/parcels_with_nodes')
rentals_to_csv('data/rentals_with_nodes')