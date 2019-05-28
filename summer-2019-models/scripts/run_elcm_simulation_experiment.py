import orca
import pandas as pd
import os; os.chdir('../')
import warnings; warnings.simplefilter('ignore')
import numpy as np

from urbansim_templates import modelmanager as mm, utils
from urbansim.models.util import columns_in_formula
from choicemodels.tools import MergedChoiceTable, monte_carlo_choices, \
    iterative_lottery_choices, parallel_lottery_choices

from scripts import datasources, models, variables

data_mode = 'csv'
local_data_dir = '/home/data/spring_2019/base/'
csv_fnames = {
    'parcels': 'parcel_attr.csv',
    'buildings': 'buildings_v2.csv',
    'jobs': 'jobs_v2.csv',
    'establishments': 'establishments_v2.csv',
    'households': 'households_v2.csv',
    'persons': 'persons_v3.csv',
    'rentals': 'MTC_craigslist_listings_7-10-18.csv',
    'units': 'units_v2.csv',
    'skims': 'skims_110118.csv',
    'drive_nodes': 'bay_area_tertiary_strongly_nodes.csv',
    'drive_edges': 'bay_area_tertiary_strongly_edges.csv',
    'drive_access_vars': 'drive_net_vars.csv',
    'walk_nodes': 'bayarea_walk_nodes.csv',
    'walk_edges': 'bayarea_walk_edges.csv',
    'walk_access_vars': 'walk_net_vars.csv',
}


def mct_callable(obs, alts):
    return MergedChoiceTable(
        obs, alts, sample_size=m.alt_sample_size)


def probs_callable(mct):
    return m.model.probabilities(mct)


if __name__ == '__main__':

    orca.add_injectable('data_mode', data_mode)
    orca.add_injectable('csv_fnames', csv_fnames)
    orca.add_injectable('store', None)
    orca.add_injectable('s3_input_data_url', None)
    orca.add_injectable('local_data_dir', local_data_dir)

    orca.run(['initialize_network_small', 'initialize_network_walk'])

    walk_net_vars = pd.read_csv(
        local_data_dir + csv_fnames['walk_access_vars'],
        index_col='osmid')
    drive_net_vars = pd.read_csv(
        local_data_dir + csv_fnames['drive_access_vars'],
        index_col='osmid')
    orca.add_table('nodeswalk', walk_net_vars)
    orca.add_table('nodessmall', drive_net_vars)

    m = mm.get_step('ELCM_finance')
    m.out_chooser_filters = ['sector_id == 52']
    m.out_alt_filters = ['non_residential_sqft > 0']

    observations = utils.get_data(
        tables=m.out_choosers,
        fallback_tables=m.choosers,
        filters=m.out_chooser_filters,
        model_expression=m.model_expression)

    alternatives = utils.get_data(
        tables=m.out_alternatives,
        fallback_tables=m.alternatives,
        filters=m.out_alt_filters,
        model_expression=m.model_expression)

    expr_cols = columns_in_formula(m.model_expression)

    obs_cols = set(observations.columns) & set(expr_cols)
    observations = observations[list(obs_cols)]

    alt_cols = set(alternatives.columns) & set(expr_cols)
    alternatives = alternatives[list(alt_cols)]
    total_alts = alternatives.shape[0]

    sample_sizes = [10, 50, 100, 500, 1000, 5000, 10000, 50000, 1e5]

    outputs = {}
    for sample_size in sample_sizes:

        print(
            'Generating marginal probabilities using a '
            'sample size of {0}'.format(str(sample_size)))

        m.alt_sample_size = sample_size
        sampling_rate = m.alt_sample_size / total_alts
        full_batch_ram = sample_size * 8.8  # estimated size in MB
        max_ram_mb = 75000

        try:
            if full_batch_ram > max_ram_mb:

                choosers = observations.copy()
                chooser_batch_size = np.floor(
                    choosers.shape[0] * (max_ram_mb / full_batch_ram))

                alts = alternatives.copy()
                len_choosers = len(choosers)
                choices_made = 0
                iter = 0

                max_marginals = np.array([])
                median_marginals = np.array([])
                stddev_marginals = np.array([])

                while (choices_made < len_choosers):

                    iter += 1
                    sampled_choosers = choosers.sample(
                        int(min(chooser_batch_size, len(choosers))))

                    mct = mct_callable(sampled_choosers, alts)

                    iter_probabilities = probs_callable(mct)
                    iter_est_marginals = iter_probabilities * sampling_rate

                    iter_max_marginals = iter_est_marginals.groupby(
                        level=0).max().values.squeeze()
                    max_marginals = np.concatenate((
                        max_marginals, iter_max_marginals))

                    iter_median_marginals = iter_est_marginals.groupby(
                        level=0).median().values.squeeze()
                    median_marginals = np.concatenate((
                        median_marginals, iter_median_marginals))

                    iter_stddev_marginals = iter_est_marginals.groupby(
                        level=0).std().values.squeeze()
                    stddev_marginals = np.concatenate((
                        stddev_marginals, iter_stddev_marginals))

                    choices_made += len(sampled_choosers)
                    choosers = choosers.drop(sampled_choosers.index.values)

                    print(
                        "Iteration {}: {} of {} valid choices".format(
                            iter, choices_made, len_choosers))

                    if len(mct.to_frame()) == 0:
                        print("No valid alts for the remaining choosers")
                        break
            else:
                choicetable = mct_callable(observations, alternatives)
                probabilities = probs_callable(choicetable)
                est_marginal_probs = probabilities * sampling_rate
                max_marginals = est_marginal_probs.groupby(level=0).max()
                median_marginals = est_marginal_probs.groupby(level=0).median()
                stddev_marginals = est_marginal_probs.groupby(level=0).std()

        except MemoryError:
            print('MemoryError at sample size = {0}'.format(
                str(sample_size)))
            break

        mean_max = np.mean(max_marginals)
        mean_median = np.mean(median_marginals)
        mean_stddev = np.mean(stddev_marginals)
        outputs[sample_size] = {
            'avg_max': mean_max, 'avg_median': mean_median,
            'avg_stddev': mean_stddev}
        out_df = pd.DataFrame.from_dict(outputs, orient='index')
        out_df.to_csv('./data/sampling_results.csv')
