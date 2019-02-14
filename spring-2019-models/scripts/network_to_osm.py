import pandas as pd
from lxml import etree
from tqdm import tqdm
import sys


node_attrs = [
    'id', 'timestamp', 'uid', 'user', 'version', 'changeset', 'lat', 'lon']
edge_attrs = ['id', 'timestamp', 'uid', 'user', 'version', 'changeset']
edge_tags = ['highway', 'lanes', 'maxspeed', 'name', 'oneway']


def pre_process_nodes(nodes):

    # convert NaNs to string
    nodes.fillna('', inplace=True)

    # rename columns per osm specification
    nodes.rename(columns={'osmid': 'id', 'x': 'lon', 'y': 'lat'}, inplace=True)

    # add empty columns for attributes not already in the df
    for attr in node_attrs:
        if attr not in nodes.columns:
            nodes[attr] = ''

    # convert all datatypes to str
    nodes = nodes.applymap(str)

    return nodes


def pre_process_edges(edges):

    # convert NaNs to string
    edges.fillna('', inplace=True)

    # rename columns per osm specification
    edges.rename(columns={'index': 'id'}, inplace=True)

    # add empty columns for attributes/tags not already in the df
    for attr in edge_attrs + edge_tags:
        if attr not in edges.columns:
            edges[attr] = ''

    # convert all datatypes to str
    edges = edges.applymap(str)

    return edges


def make_osm_root_element():
    root = etree.Element('osm')
    return root


def append_nodes(rootElement, nodes):

    for i, row in tqdm(nodes.iterrows(), total=len(nodes)):
        node = etree.SubElement(
            rootElement, 'node', attrib=row[node_attrs].to_dict())
        etree.SubElement(
            node, 'tag', attrib={'k': 'highway', 'v': row['highway']})


def append_edges(rootElement, edges):

    for i, row in tqdm(edges.iterrows(), total=len(edges)):
        edge = etree.SubElement(
            rootElement, 'way', attrib=row[edge_attrs].to_dict())
        etree.SubElement(edge, 'nd', attrib={'ref': row['u']})
        etree.SubElement(edge, 'nd', attrib={'ref': row['v']})
        for tag in edge_tags:
            etree.SubElement(edge, 'tag', attrib={tag: row[tag]})


def write_to_osm(rootElement, outpath):
    et = etree.ElementTree(rootElement)
    et.write(outpath, pretty_print=True)


if __name__ == "__main__":

    nodes = pd.read_csv(sys.argv[1])
    edges = pd.read_csv(sys.argv[2]).reset_index()
    outpath = sys.argv[3]

    processed_nodes = pre_process_nodes(nodes)
    processed_edges = pre_process_edges(edges)
    root = make_osm_root_element()
    append_nodes(root, processed_nodes)
    append_edges(root, processed_edges)

    write_to_osm(root, outpath)
