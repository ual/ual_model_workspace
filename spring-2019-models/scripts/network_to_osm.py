import pandas as pd
from lxml import etree
from tqdm import tqdm
import sys


nodes = pd.read_csv(sys.argv[1])
edges = pd.read_csv(sys.argv[2]).reset_index()

nodes.fillna('', inplace=True)
edges.fillna('', inplace=True)

nodes.rename(columns={'osmid': 'id', 'x': 'lon', 'y': 'lat'}, inplace=True)

nodes['timestamp'] = ''
nodes['uid'] = ''
nodes['user'] = ''
nodes['version'] = ''
nodes['changeset'] = ''

nodes['id'] = nodes['id'].astype(str)
nodes['lon'] = nodes['lon'].astype(str)
nodes['lat'] = nodes['lat'].astype(str)

edges['timestamp'] = ''
edges['uid'] = ''
edges['user'] = ''
edges['version'] = ''
edges['changeset'] = ''

edges['index'] = edges['index'].astype(str)
edges['u'] = edges['u'].astype(str)
edges['v'] = edges['v'].astype(str)
edges['lanes'] = edges['lanes'].astype(str)
edges['maxspeed'] = edges['maxspeed'].astype(str)
edges['oneway'] = edges['oneway'].astype(str)

edges.rename(columns={'index': 'id'}, inplace=True)

root = etree.Element('osm')
node_attrs = [
    'id', 'timestamp', 'uid', 'user', 'version', 'changeset', 'lat', 'lon']
edge_attrs = ['id', 'timestamp', 'uid', 'user', 'version', 'changeset']
edge_tags = ['highway', 'lanes', 'maxspeed', 'name', 'oneway']

for i, row in tqdm(nodes.iterrows(), total=len(nodes)):
    node = etree.SubElement(root, 'node', attrib=row[node_attrs].to_dict())
    tag = etree.SubElement(
        node, 'tag', attrib={'k': 'highway', 'v': row['highway']})

for i, row in tqdm(edges.iterrows(), total=len(edges)):
    edge = etree.SubElement(root, 'way', attrib=row[edge_attrs].to_dict())
    nd_u = etree.SubElement(edge, 'nd', attrib={'ref': row['u']})
    nd_v = etree.SubElement(edge, 'nd', attrib={'ref': row['v']})
    for tag in edge_tags:
        etree.SubElement(edge, 'tag', attrib={tag: row[tag]})

et = etree.ElementTree(root)
et.write(sys.argv[3], pretty_print=True)
