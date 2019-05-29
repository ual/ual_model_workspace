import orca
from urbansim.utils import misc

import pandas as pd
import numpy as np

############################
# small drive network vars #
############################


@orca.column('parcels')
def node_id_small(parcels, netsmall):
    idssmall_parcel = netsmall.get_node_ids(parcels.x, parcels.y)
    return idssmall_parcel


@orca.column('rentals')
def node_id_small(rentals, netsmall):
    idssmall_rentals = netsmall.get_node_ids(
        rentals.longitude, rentals.latitude)
    return idssmall_rentals


# @orca.column('buildings')
# def node_id_small(parcels, buildings):
#     return misc.reindex(parcels.node_id_small, buildings.parcel_id)


@orca.column('units')
def node_id_small(buildings, units):
    return misc.reindex(buildings.node_id_small, units.building_id)


@orca.column('households')
def node_id_small(units, households):
    return misc.reindex(units.node_id_small, households.unit_id)


@orca.column('persons')
def node_id_small(households, persons):
    return misc.reindex(households.node_id_small, persons.household_id)


@orca.column('jobs')
def node_id_small(buildings, jobs):
    return misc.reindex(buildings.node_id_small, jobs.building_id)


###########################
#    walk network vars    #
###########################
@orca.column('parcels')
def node_id_walk(parcels, netwalk):
    idswalk_parcel = netwalk.get_node_ids(parcels.x, parcels.y)
    return idswalk_parcel


@orca.column('rentals')
def node_id_walk(rentals, netwalk):
    idswalk_rentals = netwalk.get_node_ids(rentals.longitude, rentals.latitude)
    return idswalk_rentals


# @orca.column('buildings')
# def node_id_walk(parcels, buildings):
#     return misc.reindex(parcels.node_id_walk, buildings.parcel_id)


@orca.column('units')
def node_id_walk(buildings, units):
    return misc.reindex(buildings.node_id_walk, units.building_id)


@orca.column('households')
def node_id_walk(units, households):
    return misc.reindex(units.node_id_walk, households.unit_id)


@orca.column('persons')
def node_id_walk(households, persons):
    return misc.reindex(households.node_id_walk, persons.household_id)


@orca.column('jobs')
def node_id_walk(buildings, jobs):
    return misc.reindex(buildings.node_id_walk, jobs.building_id)


##########################
# small network aggregation
##########################

def fill_median(Series): # replace inf and NaN with median
    return Series.replace([np.inf, -np.inf],np.nan).fillna(Series.median())

@orca.column('nodessmall')
def pop_jobs_ratio_10000(nodessmall):
    return fill_median(nodessmall['pop_10000'] / nodessmall['jobs_10000'])
    
@orca.column('nodessmall')
def pop_jobs_ratio_25000(nodessmall):
    return fill_median(nodessmall['pop_25000'] / nodessmall['jobs_25000'])                

##########################
# walk network aggregation
##########################

@orca.column('nodeswalk')
def prop_children_500_walk(nodeswalk):
    return fill_median((nodeswalk['children_500_walk'] > 0).astype(int) / nodeswalk['hh_500_walk'])

@orca.column('nodeswalk')
def prop_singles_500_walk (nodeswalk):
    return fill_median(nodeswalk['singles_500_walk'] / nodeswalk['hh_500_walk'])

@orca.column('nodeswalk')
def prop_elderly_500_walk (nodeswalk):
    return fill_median(nodeswalk['elderly_hh_500_walk'] / nodeswalk['hh_500_walk'])

@orca.column('nodeswalk')
def prop_black_500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_black_500_walk'] / nodeswalk['pop_500_walk'])

@orca.column('nodeswalk')
def prop_white_500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_white_500_walk'] / nodeswalk['pop_500_walk'])

@orca.column('nodeswalk')
def prop_asian_500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_asian_500_walk'] / nodeswalk['pop_500_walk'])

@orca.column('nodeswalk')
def prop_hisp_500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_hisp_500_walk'] / nodeswalk['pop_500_walk'])

@orca.column('nodeswalk')
def prop_rich_500_walk (nodeswalk):
    return fill_median(nodeswalk['rich_500_walk'] / nodeswalk['pop_500_walk'])

@orca.column('nodeswalk')
def prop_poor_500_walk (nodeswalk):
    return fill_median(nodeswalk['poor_500_walk'] / nodeswalk['pop_500_walk'])

@orca.column('nodeswalk')
def prop_children_1500_walk (nodeswalk):
    return fill_median((nodeswalk['children_1500_walk'] > 0).astype(int)/nodeswalk['hh_1500_walk'])

@orca.column('nodeswalk')
def prop_singles_1500_walk (nodeswalk):
    return fill_median(nodeswalk['singles_1500_walk'] / nodeswalk['hh_1500_walk'])

@orca.column('nodeswalk')
def prop_elderly_1500_walk (nodeswalk):
    return fill_median(nodeswalk['elderly_hh_1500_walk'] / nodeswalk['hh_1500_walk'])

@orca.column('nodeswalk')
def prop_black_1500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_black_1500_walk'] / nodeswalk['pop_1500_walk'])

@orca.column('nodeswalk')
def prop_white_1500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_white_1500_walk'] / nodeswalk['pop_1500_walk'])

@orca.column('nodeswalk')
def prop_asian_1500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_asian_1500_walk'] / nodeswalk['pop_1500_walk'])

@orca.column('nodeswalk')
def prop_hisp_1500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_hisp_1500_walk'] / nodeswalk['pop_1500_walk'])

@orca.column('nodeswalk')
def prop_rich_1500_walk (nodeswalk):
    return fill_median(nodeswalk['rich_1500_walk'] / nodeswalk['pop_1500_walk'])

@orca.column('nodeswalk')
def prop_poor_1500_walk (nodeswalk):
    return fill_median(nodeswalk['poor_1500_walk'] / nodeswalk['pop_1500_walk'])

@orca.column('nodeswalk')
def pop_jobs_ratio_1500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_1500_walk'] / (nodeswalk['jobs_500_walk']))

@orca.column('nodeswalk')
def avg_hhs_500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_500_walk'] / (nodeswalk['hh_500_walk']))

@orca.column('nodeswalk')
def avg_hhs_1500_walk (nodeswalk):
    return fill_median(nodeswalk['pop_1500_walk'] / (nodeswalk['hh_1500_walk']))

###########################
#    beam network vars    #
###########################
# @orca.column('parcels')
# def node_id_beam(parcels, netbeam):
#     idsbeam_parcel = netbeam.get_node_ids(parcels.x, parcels.y)
#     return idsbeam_parcel


# @orca.column('rentals')
# def node_id_beam(rentals, netbeam):
#     idsbeam_rentals = netbeam.get_node_ids(
#         rentals.longitude, rentals.latitude)
#     return idsbeam_rentals


# @orca.column('buildings')
# def node_id_beam(parcels, buildings):
#     return misc.reindex(parcels.node_id_beam, buildings.parcel_id)


# @orca.column('jobs')
# def node_id_beam(buildings, jobs):
#     return misc.reindex(buildings.node_id_beam, jobs.building_id)


###############################
#      WLCM dummy columns     #
###############################

@orca.column('jobs')
def sector_retail(jobs):
    return jobs['sector_id'].isin([44, 45]).astype(int)


@orca.column('jobs')
def sector_healthcare(jobs):
    return jobs['sector_id'].isin([62]).astype(int)


@orca.column('jobs')
def sector_tech(jobs):
    return jobs['sector_id'].isin([51, 54]).astype(int)


@orca.column('jobs')
def sector_food_and_hosp(jobs):
    return jobs['sector_id'].isin([72]).astype(int)


@orca.column('jobs')
def sector_mfg(jobs):
    return jobs['sector_id'].isin([31, 32, 33]).astype(int)


@orca.column('jobs')
def sector_edu_serv(jobs):
    return jobs['sector_id'].isin([61]).astype(int)


@orca.column('jobs')
def sector_oth_serv(jobs):
    return jobs['sector_id'].isin([81]).astype(int)


@orca.column('jobs')
def sector_constr(jobs):
    return jobs['sector_id'].isin([23]).astype(int)


@orca.column('jobs')
def sector_gov(jobs):
    return jobs['sector_id'].isin([92]).astype(int)


@orca.column('jobs')
def sector_fire(jobs):
    return jobs['sector_id'].isin([52, 53]).astype(int)


@orca.column('jobs')
def sector_whlsale(jobs):
    return jobs['sector_id'].isin([42]).astype(int)


@orca.column('jobs')
def sector_admin(jobs):
    return jobs['sector_id'].isin([56]).astype(int)


@orca.column('jobs')
def sector_transport(jobs):
    return jobs['sector_id'].isin([48]).astype(int)


@orca.column('jobs')
def sector_arts(jobs):
    return jobs['sector_id'].isin([71]).astype(int)


@orca.column('jobs')
def sector_util(jobs):
    return jobs['sector_id'].isin([22]).astype(int)


@orca.column('jobs')
def parcel_id(jobs, buildings):
    return misc.reindex(
        buildings.parcel_id, jobs.building_id)


@orca.column('persons')
def no_higher_ed(persons):
    return (persons['edu'] < 21).astype(int)


@orca.column('persons')
def age_under_45(persons):
    return (persons['age'] < 45).astype(int)


@orca.column('households')
def hh_inc_under_25k(households):
    return ((
        households['income'] < 25000) & (
        households['income'] > 10)).astype(int)


@orca.column('households')
def hh_inc_25_to_75k(households):
    return ((
        households['income'] >= 25000) & (
        households['persons'] < 75000)).astype(int)


@orca.column('households')
def hh_inc_75_to_200k(households):
    return ((
        households['income'] >= 75000) & (
        households['income'] < 200000)).astype(int)


# cols for WLCM interaction terms
@orca.column('jobs')
def zone_id_work(jobs, parcels):
    return misc.reindex(
        parcels.zone_id, jobs.parcel_id)


@orca.column('persons')
def zone_id_home(persons, households, units, buildings, parcels):
    return misc.reindex(
        orca.merge_tables(
            households, [households, units, buildings, parcels],
            columns=['zone_id'])['zone_id'],
        persons.household_id).astype(float)


#########################################
#      Auto ownership dummy columns     #
#########################################


# income bin dummies
@orca.column('households')
def income_2(households):
    return ((households['income']>= 0) & (households['income']<= 20000)).astype(int)


@orca.column('households')
def income_4(households):
    return ((households['income']> 20000) & (households['income']<= 40000)).astype(int)


@orca.column('households')
def income_6(households):
    return ((households['income']> 40000) & (households['income']<= 60000)).astype(int)


@orca.column('households')
def income_8(households):
    return ((households['income']> 60000) & (households['income']<= 80000)).astype(int)


@orca.column('households')
def income_10(households):
    return ((households['income']> 80000) & (households['income']<= 100000)).astype(int)


@orca.column('households')
def income_12(households):
    return ((households['income']> 100000) & (households['income']<= 120000)).astype(int)


@orca.column('households')
def income_12p(households):
    return (households['income']> 120000).astype(int)


# tenure type dummies
@orca.column('households')
def tenure_1(households):
    return (households['tenure'] == 1).astype(int)


@orca.column('households')
def tenure_2(households):
    return (households['tenure'] == 2).astype(int)


@orca.column('households')
def tenure_3(households):
    return (households['tenure'] == 3).astype(int)


@orca.column('households')
def tenure_4(households):
    return (households['tenure'] == 4).astype(int)


@orca.column('households')
def single_family_int(households):
    return households['single_family'].astype(int)


@orca.column('households')
def building_type_2(households):
    return (households['building_type'] == 2).astype(int)


# AM Peak Accessibility Vars

@orca.column('parcels')
def average_income_20(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.average_income_20, parcels.block_id)


@orca.column('parcels')
def above_jobs_20(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.above_jobs_20, parcels.block_id)


@orca.column('parcels')
def above_jobs_40(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.above_jobs_40, parcels.block_id)


@orca.column('parcels')
def above_jobs_60(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.above_jobs_60, parcels.block_id)


@orca.column('parcels')
def below_jobs_20(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.below_jobs_20, parcels.block_id)


@orca.column('parcels')
def below_jobs_40(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.below_jobs_40, parcels.block_id)


@orca.column('parcels')
def below_jobs_60(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.below_jobs_60, parcels.block_id)


@orca.column('parcels')
def employment_20(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.employment_20, parcels.block_id)


@orca.column('parcels')
def employment_40(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.employment_40, parcels.block_id)


@orca.column('parcels')
def employment_60(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.employment_60, parcels.block_id)


@orca.column('parcels')
def population_20(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.population_20, parcels.block_id)


@orca.column('parcels')
def population_40(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.population_40, parcels.block_id)


@orca.column('parcels')
def population_60(parcels, access_indicators_ampeak):
    return misc.reindex(
        access_indicators_ampeak.population_60, parcels.block_id)

###########################
#  TOD choice dummy vars  #
###########################
@orca.column('households')
def hh_inc_150kplus(households):
    return((
        households['income'] > 150000) | (
        households['income'] == 150000)).astype(int)

@orca.column('persons')
def lessGED(persons):
    return(persons['edu'] < 16).astype(int)

@orca.column('persons')
def GED(persons):
    return(persons['edu'].isin([16,17])).astype(int)

@orca.column('persons')
def somebach(persons):
    return(persons['edu'].isin([16,17])).astype(int)

@orca.column('persons')
def Assoc(persons):
    return(persons['edu'].isin([20])).astype(int)
           
@orca.column('persons')
def Bach(persons):
    return(persons['edu'].isin([21])).astype(int)
           
@orca.column('persons')
def female(persons):
    return (persons['sex'] - 1)
           
@orca.column('persons')
def white(persons):
    return(persons['race_id'].isin([1.0])).astype(int)

@orca.column('persons')
def minority(persons):
    return(persons['white'].isin([0.0])).astype(int)
           
@orca.column('persons')
def age_16less25(persons):
    return((persons.age.between(16,25,inclusive = False)) | (persons.age==16)).astype(int)
           
@orca.column('households')
def hh_size_1per(households):
    return(households.persons.isin([1.0])).astype(int)
           
@orca.column('jobs')
def finance(jobs):
    return jobs['sector_id'].isin([52]).astype(int)
           
@orca.column('jobs')
def info(jobs):
    return jobs['sector_id'].isin([51]).astype(int)
           
@orca.column('jobs')
def scitech(jobs):
    return jobs['sector_id'].isin([54]).astype(int)
