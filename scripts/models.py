import orca
import pandana as pdna
import pandas as pd
from urbansim.utils import misc, networks

# Set data directory

d = 'data/'

if 'data_directory' in orca.list_injectables():
    d = orca.get_injectable('data_directory')

@orca.step()
def test_manual_registration():
    print("Model step is running")


@orca.step()
def initialize_network():
    """
    This will be turned into a data loading template.
    
    """
    @orca.injectable('net', cache=True)
    def build_network():
        nodes = pd.read_csv(d + 'bay_area_tertiary_strongly_nodes.csv')\
                .set_index('osmid')
        edges = pd.read_csv(d + 'bay_area_tertiary_strongly_edges.csv')
        net = pdna.Network(nodes.x, nodes.y, edges.u, edges.v, edges[['length']])
        net.precompute(5000)
        return net
    
    # Assign 'node_id' to the parcels
    
    parcels = orca.get_table('parcels').to_frame(columns=['x','y'])
    ids = orca.get_injectable('net').get_node_ids(parcels.x, parcels.y)
    orca.get_table('parcels').update_col_from_series('node_id', ids, cast=True)
    
     # Assign 'node_id' to the sales

    # sales = orca.get_table('sales').to_frame(columns=['sa_x_coord','sa_y_coord'])
    # ids = orca.get_injectable('net').get_node_ids(sales.sa_x_coord, sales.sa_y_coord)
    # orca.get_table('sales').update_col_from_series('node_id', ids, cast=True )
    
    # Anticipating that a 'nodes' table will be built, specify a broadcast relationship
    # (how to handle this best in a template?)
    
    orca.broadcast('nodes', 'parcels', cast_index=True, onto_on='node_id')
#    orca.broadcast('nodes', 'sales', cast_index=True, onto_on='node_id')
    
    # Also assign 'node_id' down to the other tables - this is required for calculating 
    # node-level aggregations of variables from a table

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

    @orca.column('jobs', 'node_id')
    def node_id(buildings, jobs):
        return misc.reindex(buildings.node_id, jobs.building_id)
    
    
    # While we're at it, we can use these node_id columns to define direct broadcasts
    # between the nodes table and lower-level ones, which speeds up merging
    
    orca.broadcast('nodes', 'units', cast_index=True, onto_on='node_id')


@orca.step()
def network_aggregations(net):
    """
    This will be turned into a network aggregation template.
    
    """
    nodes = networks.from_yaml(net, 'network_aggregations.yaml')
    nodes = nodes.fillna(0)
    print(nodes.describe())
    orca.add_table('nodes', nodes)
