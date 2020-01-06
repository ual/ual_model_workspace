import orca
import warnings

import urbansim_templates

from scripts import models, datasources, variables

warnings.simplefilter('ignore')

orca.add_injectable(
    'data_directory', '/home/data/fall_2018/')
orca.add_injectable(
    'beam_network_dir', '/home/data/spring_2019/beam_to_urbansim-v2/')

if __name__ == "__main__":

    model_steps = [
        'initialize_network_beam',
        'initialize_network_walk',
        'network_aggregations_beam',
        # 'network_aggregations_walk',
        # 'wlcm_simulate',
        # 'TOD_choice_simulate',
        # 'auto_ownership_simulate',
        # 'primary_mode_choice_simulate',
        # 'TOD_distribution_simulate',
        # 'generate_activity_plans'
    ]

    orca.run(model_steps)
