import pandas as pd
import patsy
import numpy as np

from urbansim_templates import modelmanager as mm
from urbansim_templates.models import LargeMultinomialLogitStep
import orca
import os; os.chdir('../')
import warnings;warnings.simplefilter('ignore')
from scripts import datasources, models, variables
from choicemodels import MultinomialLogit
from choicemodels import mnl
from choicemodels.tools import MergedChoiceTable

orca.run(['initialize_network_small'])#, 'network_aggregations_small'])
orca.run(['initialize_network_walk'])#, 'network_aggregations_walk'])

# persons = orca.get_table('persons').to_frame()
# households = orca.get_table('households').to_frame()
# buildings = orca.get_table('buildings').to_frame()
# parcels = orca.get_table('parcels').to_frame()
# jobs = orca.get_table('jobs').to_frame()
interaction_terms_tt = pd.read_csv(
    './data/WLCM_interaction_terms_tt.csv', index_col=[
        'zone_id_home', 'zone_id_work'])
interaction_terms_dist = pd.read_csv(
    './data/WLCM_interaction_terms_dist.csv', index_col=[
        'zone_id_home', 'zone_id_work'])
interaction_terms_cost = pd.read_csv(
    './data/WLCM_interaction_terms_cost.csv', index_col=[
        'zone_id_home', 'zone_id_work'])
walk_net_vars = pd.read_csv('./data/walk_net_vars.csv', index_col='osmid')
drive_net_vars = pd.read_csv('./data/drive_net_vars.csv', index_col='osmid')
orca.add_table('nodeswalk', walk_net_vars)
orca.add_table('nodessmall', drive_net_vars)
print('Finished loading network aggs')
# commuters = persons[(persons['worker'] == 1) & (persons['work_at_home'] == 0)]

obs = orca.merge_tables('persons', [
    'persons', 'households', 'units', 'buildings', 'parcels']).rename(
    columns={'zone_id': 'zone_id_home'})
obs.index.name = 'obs_id'


obs = obs[[
    'zone_id_home', 'age', 'edu', 'income']]
print('Finished preparing observation data')

alts = orca.merge_tables(
    'jobs', [
        'jobs', 'buildings', 'parcels', 'nodeswalk', 'nodessmall']).rename(
    columns={'zone_id': 'zone_id_work'})



# # occupation of alternatives
# alts['occup_mgmt'] = alts['occupation_id'].isin([11]).astype(int)
# alts['occup_sales'] = alts['occupation_id'].isin([41]).astype(int)
# alts['occup_biz'] = alts['occupation_id'].isin([13]).astype(int)
# alts['occup_admin'] = alts['occupation_id'].isin([43]).astype(int)
# alts['occup_edu'] = alts['occupation_id'].isin([25]).astype(int)
# alts['occup_food'] = alts['occupation_id'].isin([35]).astype(int)
# alts['occup_health'] = alts['occupation_id'].isin([29, 31]).astype(int)
# alts['occup_tech'] = alts['occupation_id'].isin([15]).astype(int)
# alts['occup_eng'] = alts['occupation_id'].isin([17]).astype(int)
# alts['occup_transp'] = alts['occupation_id'].isin([53]).astype(int)
# alts['occup_constr'] = alts['occupation_id'].isin([47]).astype(int)

alts = alts[[
    'jobs_1500_walk_retail', 'sector_id', 'zone_id_work'
]]

print('Finished preparing choice set alternatives data')

mct = MergedChoiceTable(
    obs, alts, sample_size=10, interaction_terms=[
        interaction_terms_tt, interaction_terms_dist,
        interaction_terms_cost])
print('Finished creating merged choice table')

mct_df = mct.to_frame()

print('Finished converting merged choice table to a data frame')
mct_df['sector_retail'] = mct_df['sector_id'].isin([44, 45]).astype(int)
mct_df['sector_healthcare'] = mct_df['sector_id'].isin([62]).astype(int)
mct_df['sector_tech'] = mct_df['sector_id'].isin([51, 54]).astype(int)
mct_df['sector_food_and_hosp'] = mct_df['sector_id'].isin([72]).astype(int)
mct_df['sector_mfg'] = mct_df['sector_id'].isin([31, 32, 33]).astype(int)
mct_df['sector_edu_serv'] = mct_df['sector_id'].isin([61]).astype(int)
mct_df['sector_oth_serv'] = mct_df['sector_id'].isin([81]).astype(int)
mct_df['sector_constr'] = mct_df['sector_id'].isin([23]).astype(int)
mct_df['sector_gov'] = mct_df['sector_id'].isin([92]).astype(int)
mct_df['sector_fire'] = mct_df['sector_id'].isin([52, 53]).astype(int)
mct_df['sector_whlsale'] = mct_df['sector_id'].isin([42]).astype(int)
mct_df['sector_admin'] = mct_df['sector_id'].isin([56]).astype(int)
mct_df['sector_transport'] = mct_df['sector_id'].isin([48]).astype(int)
mct_df['sector_arts'] = mct_df['sector_id'].isin([71]).astype(int)
mct_df['sector_util'] = mct_df['sector_id'].isin([22]).astype(int)
mct_df['no_higher_ed'] = (mct_df['edu'] < 5).astype(int)
mct_df['age_under_45'] = (mct_df['age'] < 45).astype(int)
mct_df['hh_inc_under_25k'] = (mct_df['income'] < 3).astype(int)
mct_df['hh_inc_25_to_75k'] = (
    (mct_df['income'] > 2) & (mct_df['income'] < 6)).astype(int)
mct_df['hh_inc_75_to_200k'] = (
    (mct_df['income'] > 5) & (mct_df['income'] < 9)).astype(int)

print('Finished feature extraction')

mm.initialize()

m = mm.get_step('WLCM-higher_ed_x_sector-tt_x_dist-cost_x_income')

m.chooser_filters = ['age < 115', 'worker == 1', 'work_at_home == 0', 'edu < 21']

dm = patsy.dmatrix(m.model_expression, data=mct_df, return_type='dataframe')

print('Finished creating dmatrix')