import orca
import pandana as pdna
import pandas as pd
from urbansim.utils import misc, networks
from pandana.network import reserve_num_graphs

# Set data directory

d = 'data/'

if 'data_directory' in orca.list_injectables():
    d = orca.get_injectable('data_directory')

@orca.step()
def test_manual_registration():
    print("Model step is running")


reserve_num_graphs(40)

@orca.step()
def initialize_network_small():
    """
    This will be turned into a data loading template.
    
    """
    @orca.injectable('netsmall', cache=True)
    def build_networksmall():
        nodessmall = pd.read_csv(d + 'bay_area_tertiary_strongly_nodes.csv')\
                .set_index('osmid')
        edgessmall = pd.read_csv(d + 'bay_area_tertiary_strongly_edges.csv')
        netsmall = pdna.Network(nodessmall.x, nodessmall.y, edgessmall.u, \
        edgessmall.v, edgessmall[['length']], twoway=False)
        netsmall.precompute(25000)
        return netsmall

    parcels = orca.get_table('parcels').to_frame(columns=['x','y'])
    idssmall = orca.get_injectable('netsmall').get_node_ids(parcels.x, parcels.y)
    orca.add_column('parcels', 'node_id_small', idssmall, cache=False)
    orca.broadcast('nodessmall', 'parcels', cast_index=True,onto_on='node_id_small')

    rentals = orca.get_table('rentals').to_frame(columns=['lon','lat'])
    ids = orca.get_injectable('netsmall').get_node_ids(rentals.lon, rentals.lat)
    orca.add_column('rentals', 'node_id_small', ids, cache=False)

    @orca.column('buildings', 'node_id_small')
    def node_id(parcels, buildings):
        return misc.reindex(parcels.node_id_small, buildings.parcel_id)

    @orca.column('units', 'node_id_small')
    def node_id(buildings, units):
        return misc.reindex(buildings.node_id_small, units.building_id)

    @orca.column('households', 'node_id_small')
    def node_id(units, households):
        return misc.reindex(units.node_id_small, households.unit_id)

    @orca.column('persons', 'node_id_small')
    def node_id(households, persons):
        return misc.reindex(households.node_id_small, persons.household_id)

    @orca.column('jobs', 'node_id_small')
    def node_id(buildings, jobs):
        return misc.reindex(buildings.node_id_small, jobs.building_id)
    
    # While we're at it, we can use these node_id columns to define direct broadcasts
    # between the nodes table and lower-level ones, which speeds up merging
    
    orca.broadcast('nodessmall', 'units', cast_index=True, onto_on='node_id_small')


@orca.step()
def initialize_network_drive():
    """
    This will be turned into a data loading template.
    
    """
    @orca.injectable('netdrive', cache=True)
    def build_networkdrive():
        nodesdrive = pd.read_csv(d + 'bay_area_drive_full_nodes.csv')\
                .set_index('osmid')
        edgesdrive = pd.read_csv(d + 'bay_area_drive_full_edges.csv')
        netdrive = pdna.Network(nodesdrive.x, nodesdrive.y, edgesdrive.u, edgesdrive.v, \
        edgesdrive[['length']], twoway=False)
        netdrive.precompute(2500)
        return netdrive
    
    # Assign 'node_id' to the parcels
    
    parcels = orca.get_table('parcels').to_frame(columns=['x','y'])
    #orca.get_table('parcels').update_col_from_series('node_id_small', idssmall, \
    #cast=True)
    idsdrive = orca.get_injectable('netdrive').get_node_ids(parcels.x, parcels.y)
    orca.add_column('parcels', 'node_id_drive', idsdrive, cache=False)
    orca.broadcast('nodesdrive', 'parcels', cast_index=True, onto_on='node_id_drive')

    #orca.get_table('parcels').update_col_from_series('node_id_drive', idsdrive, \
    #cast=True)
    
    # Assign 'node_id' to the sales

    # sales = orca.get_table('sales').to_frame(columns=['sa_x_coord','sa_y_coord'])
    # ids = orca.get_injectable('net').get_node_ids(sales.sa_x_coord, sales.sa_y_coord)
    # orca.get_table('sales').update_col_from_series('node_id', ids, cast=True )
    
    # Assign 'node_id' to the rentals

    rentals = orca.get_table('rentals').to_frame(columns=['lon','lat'])
    ids = orca.get_injectable('netdrive').get_node_ids(rentals.lon, rentals.lat)
    orca.add_column('rentals', 'node_id_drive', ids, cache=False)
    
    # Anticipating that a 'nodes' table will be built, specify a broadcast relationship
    # (how to handle this best in a template?)
    

    #orca.broadcast('nodes', 'rentals', cast_index=True, onto_on='node_id')
    # orca.broadcast('nodes', 'sales', cast_index=True, onto_on='node_id')
    
    # Also assign 'node_id' down to the other tables - this is required for calculating 
    # node-level aggregations of variables from a table

    @orca.column('buildings', 'node_id_drive')
    def node_id(parcels, buildings):
        return misc.reindex(parcels.node_id_drive, buildings.parcel_id)

    @orca.column('units', 'node_id_drive')
    def node_id(buildings, units):
        return misc.reindex(buildings.node_id_drive, units.building_id)

    @orca.column('households', 'node_id_drive')
    def node_id(units, households):
        return misc.reindex(units.node_id_drive, households.unit_id)

    @orca.column('persons', 'node_id_drive')
    def node_id(households, persons):
        return misc.reindex(households.node_id_drive, persons.household_id)

    @orca.column('jobs', 'node_id_drive')
    def node_id(buildings, jobs):
        return misc.reindex(buildings.node_id_drive, jobs.building_id)
    
    orca.broadcast('nodesdrive', 'units', cast_index=True, onto_on='node_id_drive')


@orca.step()
def network_aggregations_drive(netdrive):
    """
    This will be turned into a network aggregation template.
    
    """

    nodesdrive = networks.from_yaml(netdrive, 'network_aggregations_drive.yaml')
    nodesdrive = nodesdrive.fillna(0)
    print(nodesdrive.describe())
    orca.add_table('nodesdrive', nodesdrive)

@orca.step()
def network_aggregations_small(netsmall):
    """
    This will be turned into a network aggregation template.
    
    """    
    nodessmall = networks.from_yaml(netsmall, 'network_aggregations_small.yaml')
    nodessmall = nodessmall.fillna(0)
    print(nodessmall.describe())
    orca.add_table('nodessmall', nodessmall)
