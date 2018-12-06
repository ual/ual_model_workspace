import orca
import pandana as pdna
import pandas as pd

from urbansim.utils import networks
from urbansim_templates import modelmanager as mm
from choicemodels import MultinomialLogitResults
from choicemodels.tools import MergedChoiceTable, simulation
# Set data directory

d = '/home/data/fall_2018/'

if 'data_directory' in orca.list_injectables():
    d = orca.get_injectable('data_directory')

mm.initialize()


@orca.step()
def test_manual_registration():
    print("Model step is running")


@orca.step()
def initialize_network_small():
    """
    This will be turned into a data loading template.
    """

    @orca.injectable('netsmall', cache=True)
    def build_networksmall():
        nodessmall = pd.read_csv(d + 'bay_area_tertiary_strongly_nodes.csv') \
            .set_index('osmid')
        edgessmall = pd.read_csv(d + 'bay_area_tertiary_strongly_edges.csv')
        netsmall = pdna.Network(nodessmall.x, nodessmall.y, edgessmall.u,
                                edgessmall.v, edgessmall[['length']],
                                twoway=False)
        netsmall.precompute(25000)
        return netsmall


@orca.step()
def initialize_network_walk():
    """
    This will be turned into a data loading template.

    """

    @orca.injectable('netwalk', cache=True)
    def build_networkwalk():
        nodeswalk = pd.read_csv(d + 'bayarea_walk_nodes.csv') \
            .set_index('osmid')
        edgeswalk = pd.read_csv(d + 'bayarea_walk_edges.csv')
        netwalk = pdna.Network(nodeswalk.x, nodeswalk.y, edgeswalk.u,
                               edgeswalk.v, edgeswalk[['length']], twoway=True)
        netwalk.precompute(2500)
        return netwalk


@orca.step()
def initialize_network_beam():
    """
    This will be turned into a data loading template.

    """

    @orca.injectable('netbeam', cache=True)
    def build_networkbeam():
        nodesbeam = pd.read_csv(d + 'physsim-network-nodes.csv') \
            .set_index('id')
        edgesbeam = pd.read_csv(d + 'physsim-network-links.csv')
        netbeam = pdna.Network(
            nodesbeam['x'], nodesbeam['y'], edgesbeam['from'],
            edgesbeam['to'], edgesbeam[['travelTime']], twoway=False)
        netbeam.precompute(7200)
        return netbeam


@orca.step()
def network_aggregations_small(netsmall):
    """
    This will be turned into a network aggregation template.
    """
    nodessmall = networks.from_yaml(
        netsmall, 'network_aggregations_small.yaml')
    nodessmall = nodessmall.fillna(0)
    print(nodessmall.describe())
    orca.add_table('nodessmall', nodessmall)


@orca.step()
def network_aggregations_walk(netwalk):
    """
    This will be turned into a network aggregation template.

    """

    nodeswalk = networks.from_yaml(netwalk, 'network_aggregations_walk.yaml')
    nodeswalk = nodeswalk.fillna(0)
    print(nodeswalk.describe())
    orca.add_table('nodeswalk', nodeswalk)


@orca.step()
def network_aggregations_beam(netbeam):
    """
    This will be turned into a network aggregation template.

    """

    nodesbeam = networks.from_yaml(netbeam, 'network_aggregations_beam.yaml')
    nodesbeam = nodesbeam.fillna(0)
    print(nodesbeam.describe())
    orca.add_table('nodesbeam', nodesbeam)


@orca.step()
def wlcm_simulate(persons):
    """
    Generate workplace location choices for the synthetic pop

    """
    interaction_terms_tt = pd.read_csv(
        './data/WLCM_interaction_terms_tt.csv', index_col=[
            'zone_id_home', 'zone_id_work'])
    interaction_terms_dist = pd.read_csv(
        './data/WLCM_interaction_terms_dist.csv', index_col=[
            'zone_id_home', 'zone_id_work'])
    interaction_terms_cost = pd.read_csv(
        './data/WLCM_interaction_terms_cost.csv', index_col=[
            'zone_id_home', 'zone_id_work'])

    m = mm.get_step(
        'WLCM_constrained-higher_ed_x_sector-tt_x_dist-cost_x_income')

    m.run(chooser_batch_size=200000, interaction_terms=[
        interaction_terms_tt, interaction_terms_dist, interaction_terms_cost])
