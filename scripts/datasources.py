import orca
import pandas as pd
import zipfile

# reading data directly from zipfiles is nice, but it doesn't work with symlinks (on my 
# Mac at least) - is there a workaround?

# data documentation: https://berkeley.app.box.com/notes/282712547032


# Set data directory

d = 'data/'

if 'data_directory' in orca.list_injectables():
    d = orca.get_injectable('data_directory')


############################################################

# Tables from MTC Bay Area UrbanSim

@orca.table(cache=True)
def parcels():
#    df = pd.read_hdf(d + 'bayarea_ual.h5', 'parcels')
    df = pd.read_csv(d + 'mtc_data_platform_format_7-6-18/' + 'parcel_attr.csv')
    return df

@orca.table(cache=True)
def buildings():
#    df = pd.read_hdf(d + 'bayarea_ual.h5', 'buildings')
    df = pd.read_csv(d + 'mtc_data_platform_format_7-6-18/' + 'buildings_v2.csv')
    return df

############################################################

# Tables of Residential Sales from Dataquick added by Paul Waddell

#@orca.table(cache=True)
#def sales():
#    z = zipfile.ZipFile(d + 'salemrg.csv.zip')
#    df = pd.read_csv(z.open('salemrg.csv'))
#    df.index.name = 'sales_id'  # first column in CSV is unnamed
#    return df

############################################################

# Table of Rental Data from  Craigslist, bayarea_urbansim added by Arezoo

@orca.table(cache=True)
def rentals():
    z = zipfile.ZipFile(d + 'MTC_craigslist_listings_7-10-18.zip')
    df = pd.read_csv(z.open('MTC_craigslist_listings_7-10-18.csv'))
    return df

############################################################

# Tables synthesized by Max Gardner

@orca.table(cache=True)
def units():
    #z = zipfile.ZipFile(d + 'units_w_tenure.zip')
    #df = pd.read_csv(z.open('units_w_tenure.csv'))
    df = pd.read_csv(d + 'mtc_data_platform_format_7-6-18/' + 'units_v2.csv')
    df.index.name = 'unit_id'  # first column in CSV is unnamed
    return df

@orca.table(cache=True)
def households():
#    z = zipfile.ZipFile(d + 'synthpop_w_units.zip')
#    df = pd.read_csv(z.open('households_w_units.csv'))
    df = pd.read_csv(d + 'mtc_data_platform_format_7-6-18/' + 'households_v2.csv')
    return df

@orca.table(cache=True)
def persons():
#    z = zipfile.ZipFile(d + 'synthpop_w_units.zip')
#    df = pd.read_csv(z.open('sfbay_persons_2018_04_16.csv'))
#    df.index.name = 'person_id'  # first column in CSV is unnamed
    df = pd.read_csv(d + 'mtc_data_platform_format_7-6-18/' + 'persons_v2.csv')
    return df

@orca.table(cache=True)
def jobs():
#    z = zipfile.ZipFile(d + 'jobs_w_occup.zip')
#    df = pd.read_csv(z.open('jobs_w_occup.csv'))
    df = pd.read_csv(d + 'mtc_data_platform_format_7-6-18/' + 'jobs_v2.csv')
    return df


############################################################

# Broadcasts, a.k.a. merge relationships

orca.broadcast('parcels', 'buildings', cast_index=True, onto_on='parcel_id')
orca.broadcast('buildings', 'units', cast_index=True, onto_on='building_id')
orca.broadcast('units', 'households', cast_index=True, onto_on='unit_id')
orca.broadcast('households', 'persons', cast_index=True, onto_on='household_id')

