import orca
import pandana as pdna
import pandas as pd
from urbansim.utils import networks

@orca.step()
def test_manual_registration():
    print("Model step is running")
    return


@orca.injectable('net', cache=True)
def build_networks():
    st = pd.HDFStore('data/2015_06_01_osm_bayarea4326.h5', 'r')
    nodes, edges = st.nodes, st.edges
    net = pdna.Network(nodes["x"], nodes["y"], edges["from"], edges["to"],
                       edges[["weight"]])
    net.precompute(3000)
    return net


@orca.step()
def network_aggregations(net):
    nodes = networks.from_yaml(net, 'network_aggregations.yaml')
    nodes = nodes.fillna(0)
    print(nodes.describe())
    orca.add_table('nodes', nodes)
