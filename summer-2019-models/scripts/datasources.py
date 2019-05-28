import orca
import pandas as pd
import numpy as np

# data documentation: https://berkeley.app.box.com/notes/282712547032


@orca.table('parcels', cache=True)
def parcels(data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('parcel_attr'))
    elif data_mode == 'h5':
        df = store['parcels']
    elif data_mode == 'csv':
        try:
            df = pd.read_csv(
                local_data_dir + csv_fnames['parcels'], index_col='parcel_id',
                dtype={'parcel_id': int, 'block_id': str, 'apn': str})
        except ValueError:
            df = pd.read_csv(
                local_data_dir + csv_fnames['parcels'], index_col='primary_id',
                dtype={'primary_id': int, 'block_id': str, 'apn': str})
    return df


@orca.table('buildings', cache=True)
def buildings(data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('buildings_v2'))
    elif data_mode == 'h5':
        df = store['buildings']
    elif data_mode == 'csv':
        df = pd.read_csv(
            local_data_dir + csv_fnames['buildings'], index_col='building_id',
            dtype={'building_id': int, 'parcel_id': int})
        df['res_sqft_per_unit'] = df[
            'residential_sqft'] / df['residential_units']
        df['res_sqft_per_unit'][df['res_sqft_per_unit'] == np.inf] = 0
    return df


@orca.table('jobs', cache=True)
def jobs(data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('jobs_v2'))
    elif data_mode == 'h5':
        df = store['jobs']
    elif data_mode == 'csv':
        try:
            df = pd.read_csv(
                local_data_dir + csv_fnames['jobs'], index_col='job_id',
                dtype={'job_id': int, 'building_id': int})
        except ValueError:
            df = pd.read_csv(
                local_data_dir + csv_fnames['jobs'], index_col=0,
                dtype={'job_id': int, 'building_id': int})
            df.index.name = 'job_id'
    return df


@orca.table('establishments', cache=True)
def establishments(
        data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('establishments_v2'))
    elif data_mode == 'h5':
        df = store['establishments']
    elif data_mode == 'csv':
        df = pd.read_csv(
            local_data_dir + csv_fnames['establishments'],
            index_col='establishment_id', dtype={
                'establishment_id': int, 'building_id': int,
                'primary_id': int})
    return df


@orca.table('households', cache=True)
def households(
        data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('households_v2'))
    elif data_mode == 'h5':
        df = store['households']
    elif data_mode == 'csv':
        try:
            df = pd.read_csv(
                local_data_dir + csv_fnames['households'],
                index_col='household_id', dtype={
                    'household_id': int, 'block_group_id': str, 'state': str,
                    'county': str, 'tract': str, 'block_group': str,
                    'building_id': int, 'unit_id': int, 'persons': float})
        except ValueError:
            df = pd.read_csv(
                local_data_dir + csv_fnames['households'],
                index_col=0, dtype={
                    'household_id': int, 'block_group_id': str, 'state': str,
                    'county': str, 'tract': str, 'block_group': str,
                    'building_id': int, 'unit_id': int, 'persons': float})
            df.index.name = 'household_id'
    return df


@orca.table('persons', cache=True)
def persons(data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('persons_v3'))
    elif data_mode == 'h5':
        df = store['persons']
    elif data_mode == 'csv':
        try:
            df = pd.read_csv(
                local_data_dir + csv_fnames['persons'], index_col='person_id',
                dtype={'person_id': int, 'household_id': int})
        except ValueError:
            df = pd.read_csv(
                local_data_dir + csv_fnames['persons'], index_col=0,
                dtype={'person_id': int, 'household_id': int})
            df.index.name = 'person_id'
    return df


@orca.table('rentals', cache=True)
def rentals(data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(
            s3_input_data_url.format('MTC_craigslist_listings_7-10-18'))
    elif data_mode == 'h5':
        df = store['craigslist']
    elif data_mode == 'csv':
        try:
            df = pd.read_csv(
                local_data_dir + csv_fnames['rentals'],
                index_col='pid', dtype={
                    'pid': int, 'date': str, 'region': str,
                    'neighborhood': str, 'rent': float, 'sqft': float,
                    'rent_sqft': float, 'longitude': float,
                    'latitude': float, 'county': str, 'fips_block': str,
                    'state': str, 'bathrooms': str})
        except ValueError:
            df = pd.read_csv(
                local_data_dir + csv_fnames['rentals'],
                index_col=0, dtype={
                    'date': str, 'region': str,
                    'neighborhood': str, 'rent': float, 'sqft': float,
                    'rent_sqft': float, 'longitude': float,
                    'latitude': float, 'county': str, 'fips_block': str,
                    'state': str, 'bathrooms': str})
            df.index.name = 'pid'
    df.rent[df.rent < 100] = 100.0
    df.rent[df.rent > 10000] = 10000.0
    df.rent_sqft[df.rent_sqft < .2] = .2
    df.rent_sqft[df.rent_sqft > 50] = 50.0
    return df


@orca.table('units', cache=True)
def units(data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('units_v2'))
    elif data_mode == 'h5':
        df = store['units']
    elif data_mode == 'csv':
        df = pd.read_csv(
            local_data_dir + csv_fnames['units'], index_col='unit_id',
            dtype={'unit_id': int, 'building_id': int})
    df.index.name = 'unit_id'
    return df


# Tables from Jayne Chang

# Append AM peak UrbanAccess transit accessibility variables to parcels table

@orca.table('access_indicators_ampeak', cache=True)
def access_indicators_ampeak(
        data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('access_indicators_ampeak'))
    elif data_mode == 'h5':
        df = store['access_indicators_ampeak']
    elif data_mode == 'csv':
        df = pd.read_csv(
            local_data_dir + csv_fnames['access_indicators_ampeak'],
            dtype={'block_id': str})
    df.block_id = df.block_id.str.zfill(15)
    df.set_index('block_id', inplace=True)
    df = df.fillna(df.median())
    return df


# Tables from Emma
@orca.table('skims', cache=True)
def skims(data_mode, store, s3_input_data_url, local_data_dir, csv_fnames):
    if data_mode == 's3':
        df = pd.read_csv(s3_input_data_url.format('skims_110118'))
    elif data_mode == 'h5':
        df = store['skims']
    elif data_mode == 'csv':
        df = pd.read_csv(local_data_dir + csv_fnames['skims'], index_col=0)
    return df


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
orca.broadcast(
    'nodesbeam', 'parcels', cast_index=True, onto_on='node_id_beam')
orca.broadcast(
    'nodesbeam', 'rentals', cast_index=True, onto_on='node_id_beam')
