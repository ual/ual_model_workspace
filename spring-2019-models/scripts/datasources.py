import orca
import numpy as np
import pandas as pd


# data documentation: https://berkeley.app.box.com/notes/282712547032


# Set data directory

d = '/home/data/fall_2018/'

if 'data_directory' in orca.list_injectables():
    d = orca.get_injectable('data_directory')

b = '/home/data/spring_2019/base/'
############################################################

# Tables from MTC Bay Area UrbanSim


@orca.table(cache=True)
def parcels():
    df = pd.read_csv(
        d + 'parcel_attr.csv',
        index_col='primary_id',
        dtype={'primary_id': int, 'block_id': str})
    return df


@orca.table(cache=True)
def buildings():
    df = pd.read_csv(
        d + 'buildings_v2.csv',
        index_col='building_id', dtype={'building_id': int, 'parcel_id': int})
    df['res_sqft_per_unit'] = df['residential_sqft'] / df['residential_units']
    df['res_sqft_per_unit'][df['res_sqft_per_unit'] == np.inf] = 0
    return df


############################################################

# Table of Rental Data from  Craigslist, bayarea_urbansim added by Arezoo

@orca.table(cache=True)
def craigslist():
    df = pd.read_csv(
        d + 'MTC_craigslist_listings_7-10-18.csv',
        index_col='pid', dtype={'pid': int})
    return df


@orca.table(cache=True)
def rentals():
    df = pd.read_csv(
        d + 'rentals_with_nodes.csv',
        index_col='pid', dtype={'pid': int, 'rent': float})
    return df


############################################################

# Tables synthesized by Max Gardner

@orca.table(cache=True)
def units():
    df = pd.read_csv(
        d + 'units_v2.csv',
        index_col='unit_id', dtype={'unit_id': int, 'building_id': int})
    return df


@orca.table(cache=True)
def households():
    df = pd.read_csv(
        d + 'households_v2.csv',
        index_col='household_id', dtype={
            'household_id': int, 'block_group_id': str, 'state': str,
            'county': str, 'tract': str, 'block_group': str,
            'building_id': int, 'unit_id': int, 'persons': float})
    return df


@orca.table(cache=True)
def persons():
    df = pd.read_csv(
        d + 'persons_v3.csv',
        index_col='person_id', dtype={'person_id': int, 'household_id': int})
    return df


@orca.table(cache=True)
def jobs():
    df = pd.read_csv(
        d + 'jobs_v2.csv',
        index_col='job_id', dtype={'job_id': int, 'building_id': int})
    return df


############################################################

# Tables from Sam Blanchard
@orca.table(cache=True)
def establishments():
    df = pd.read_csv(
        d + 'establishments_v2.csv',
        index_col='establishment_id', dtype={
            'establishment_id': int, 'building_id': int, 'primary_id': int})
    return df

############################################################


# zones table
@orca.table(cache=True)
def zones():
    df = pd.read_csv(
        b + 'zones.csv', index_col='zone_id',
        dtype={'zone_id': int})
    df.drop('tract', axis=1, inplace=True)
    return df

############################################################
# skims


# Tables from Emma
@orca.table('skims', cache=True)
def skims():
    df = pd.read_csv(d + 'skims_110118.csv', index_col=0)
    return df


@orca.table(cache=True)
def beam_drive_skims():
    """
    Load BEAM skims, convert travel time to minutes
    """
    df = pd.read_csv(
        b + 'sfbay-smart-base__2019-03-28_14-22-12/' +
        'ITERS/it.30/30.skimsExcerpt.csv')

    # morning peak
    df = df[df['period'] == 'AM']
    assert len(df) == 2114116
    df = df.rename(
        columns={'origTaz': 'from_zone_id', 'destTaz': 'to_zone_id'})
    df = df.set_index(['from_zone_id', 'to_zone_id'])

    # seconds to minutes
    df['gen_tt_CAR'] = df['generalizedTimeInS'] / 60
    return df


@orca.table(cache=True)
def beam_skims():
    """
    Load BEAM skims, convert travel time to minutes
    """
    df = pd.read_csv(
        b + 'sfbay-smart-base__2019-03-28_14-22-12/' +
        'ITERS/it.30/30.skims.csv')

    df.rename(columns={
        'generalizedCost': 'gen_cost', 'origTaz': 'from_zone_id',
        'destTaz': 'to_zone_id'}, inplace=True)

    # seconds to minutes
    df['gen_tt'] = df['generalizedTimeInS'] / 60

    return df

############################################################
# Broadcasts, a.k.a. merge relationships


orca.broadcast(
    'parcels', 'buildings', cast_index=True, onto_on='parcel_id')
orca.broadcast(
    'buildings', 'units', cast_index=True, onto_on='building_id')
orca.broadcast(
    'units', 'households', cast_index=True, onto_on='unit_id')
orca.broadcast(
    'households', 'persons', cast_index=True, onto_on='household_id')
orca.broadcast(
    'buildings', 'jobs', cast_index=True, onto_on='building_id')
orca.broadcast(
    'buildings', 'establishments', cast_index=True, onto_on='building_id')
orca.broadcast(
    'nodeswalk', 'parcels', cast_index=True, onto_on='node_id_walk')
orca.broadcast(
    'nodeswalk', 'rentals', cast_index=True, onto_on='node_id_walk')
orca.broadcast(
    'nodessmall', 'rentals', cast_index=True, onto_on='node_id_small')
orca.broadcast(
    'nodessmall', 'parcels', cast_index=True, onto_on='node_id_small')
# orca.broadcast(
#     'nodesbeam', 'parcels', cast_index=True, onto_on='node_id_beam')
