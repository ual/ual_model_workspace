import orca
import pandas as pd
import zipfile
from urbansim.utils import misc

# reading data directly from zipfiles is nice, but it doesn't work with symlinks (on my 
# Mac at least) - is there a workaround?

# data documentation: https://berkeley.app.box.com/notes/282712547032


############################################################

# Tables from MTC Bay Area UrbanSim

@orca.table(cache=True)
def parcels():
    df = pd.read_hdf('data/bayarea_ual.h5', 'parcels')
    return df

@orca.table(cache=True)
def buildings():
    df = pd.read_hdf('data/bayarea_ual.h5', 'buildings')
    return df


############################################################

# Tables synthesized by Max Gardner

@orca.table(cache=True)
def units():
    z = zipfile.ZipFile('data/units_w_tenure.zip')
    df = pd.read_csv(z.open('units_w_tenure.csv'))
    return df

@orca.table(cache=True)
def households():
    z = zipfile.ZipFile('data/synthpop_w_units.zip')
    df = pd.read_csv(z.open('households_w_units.csv'))
    return df

@orca.table(cache=True)
def persons():
    z = zipfile.ZipFile('data/synthpop_w_units.zip')
    df = pd.read_csv(z.open('sfbay_persons_2018_04_16.csv'))
    return df


############################################################

# Broadcasts, a.k.a. merge relationships

orca.broadcast('nodes', 'buildings', cast_index=True, onto_on='node_id')
orca.broadcast('buildings', 'units', cast_index=True, onto_on='building_id')
orca.broadcast('units', 'households', cast_index=True, onto_on='unit_id')
orca.broadcast('households', 'persons', cast_index=True, onto_on='household_id')


############################################################

# Assign 'node_id' down to the other tables - this seems to be required for the network
# aggregations

@orca.column('buildings', 'node_id')
def node_id(parcels, buildings):
    return misc.reindex(parcels.node_id, buildings.parcel_id)

@orca.column('units', 'node_id')
def node_id(buildings, units):
    return misc.reindex(buildings.node_id, units.building_id)

@orca.column('households', 'node_id')
def node_id(units, households):
    return misc.reindex(units.node_id, households.unit_id)

@orca.column('persons', 'node_id')
def node_id(households, persons):
    return misc.reindex(households.node_id, persons.household_id)
