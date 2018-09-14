import orca
import numpy as np
import pandas as pd


# data documentation: https://berkeley.app.box.com/notes/282712547032


# Set data directory

d = '/home/data/fall_2018/'

if 'data_directory' in orca.list_injectables():
    d = orca.get_injectable('data_directory')


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
        index_col='pid', dtype={'pid': int})
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
            'househould_id': int, 'block_group_id': str, 'state': str,
            'county': str, 'tract': str, 'block_group': str,
            'building_id': int, 'unit_id': int})
    return df


@orca.table(cache=True)
def persons():
    df = pd.read_csv(
        d + 'persons_v2.csv',
        index_col='person_id', dtype={'person_id': int, 'household_id': int})
    return df


@orca.table(cache=True)
def jobs():
    df = pd.read_csv(
        d + 'jobs_v2.csv',
        index_col='job_id', dtype={'job_id': int, 'building_id': int})
    return df


############################################################

# Broadcasts, a.k.a. merge relationships

orca.broadcast('parcels', 'buildings', cast_index=True, onto_on='parcel_id')
orca.broadcast('buildings', 'units', cast_index=True, onto_on='building_id')
orca.broadcast('units', 'households', cast_index=True, onto_on='unit_id')
orca.broadcast(
    'households', 'persons', cast_index=True, onto_on='household_id')
orca.broadcast('buildings', 'jobs', cast_index=True, onto_on='building_id')
