import numpy as np
import pandas as pd
import pandana as pdna
import geopandas as gp
import matplotlib.pyplot as plt
# %matplotlib inline

homedata_file_path = '/home/data/'
dd = '/home/data/spring_2019/base/'
shapefiles_path = '/home/simon/spatial-data/'
model_outputs_path = '/home/data/spring_2019/outputs/'

def get_data():
    '''gets all relevant tables from the HDF5 and saves them to a dictionary that is indexed by 1) year and 
    2) table name. Closes the store. The function is assigned to the global variable data_dict'''
    data_dict = {}
    hdfstore = pd.HDFStore(model_outputs_path+'model_data_output.h5', mode='r') #sometimes doesnt work with a relative file path
    for year in [2010, 2015, 2025]:
        persons = hdfstore["/{}/persons".format(year)]
        hh = hdfstore["/{}/households".format(year)]
        buildings = hdfstore["/{}/buildings".format(year)]
        parcels = hdfstore["/{}/parcels".format(year)]
        jobs = hdfstore["/{}/jobs".format(year)]
        data_dict[year] = {"hh": hh, "buildings": buildings, "parcels": parcels, "jobs": jobs, "persons": persons}
    print("closing store")
    hdfstore.close()
    return data_dict

data_dict = get_data()
    
def get_merged_data(year):
    '''merges the household and buildings and parcels and persons tables together in an inner merge, 
    resulting in a dataframe with every person, their household information and their geographic information
    like block group id and parcel id, and node id'''
        
    print("merging buildings to parcels")
    try:
        buildings = data_dict[year]["buildings"].reset_index()[["building_id", "parcel_id"]]
        parcels = data_dict[year]["parcels"].reset_index()[["parcel_id", "county_id", "node_id"]]
        bldg_parc = pd.merge(buildings, parcels, on="parcel_id")
        hh = data_dict[year]["hh"]
        persons = data_dict[year]["persons"]
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()
    
    print("merging households to buildings and parcels table")
    
    hh_build = pd.merge(hh, bldg_parc, on="building_id")
    
    print("merging households to buildings")

    hh_build.index.name = "household_id"
    
    hh_build = hh_build.reset_index()
    
    

    print("merging persons to households and buildings")
    persons = data_dict[year]["persons"]
    persons.index.name = "person_id"
    
    buildings_persons = pd.merge(persons, hh_build, on='household_id')
    print("hh build table has ", len(hh_build), "rows")
    
    buildings_persons["block_group_id"] = buildings_persons["block_group_id"].apply(lambda x: "0"+x)
    buildings_persons["census_tract"] = buildings_persons["block_group_id"].apply(lambda x: x[:-1])
    return buildings_persons


def get_job_locations(year):
    '''get the location of the jobs by merging the jobs table with the buildings table on building_id and that
    table with the parcels table on parcel_id, resulting in each job being assigned to a node id to be used
    in the pandana network'''
    
    buildings = data_dict[year]['buildings'].reset_index()
    jobs = data_dict[year]['jobs'].reset_index()
    parcels = data_dict[year]['parcels'].reset_index()
    
    print("merging buildings to jobs")
    jobs_buildings = pd.merge(buildings, jobs, on='building_id')
    
    print("merging buildings with jobs to parcels")
    jobs_merge = pd.merge(jobs_buildings, parcels, on='parcel_id')
    return jobs_merge


def get_workers_by_race(year):
    '''Get the number of workers for each race by node, for a given year. Returns a dataframe
    with a column for each race and the number of workers assigned to that node by race. The node assignments
    are obtained from the person-> parcel match in get_merged_data()'''
    
    node_df_lol = []
    node_id_list = []
    df = get_merged_data(year)
    for node_id, node_df in df.groupby("node_id"):
        nhwhite_workers = sum((node_df["race_id"] == 1) & (node_df["hispanic"] == 1) & (node_df["worker"] == 1))
        nhblack_workers = sum((node_df["race_id"] == 2) & (node_df["hispanic"] == 1) & (node_df["worker"] == 1))
        nhasian_workers = sum((node_df["race_id"] == 6) & (node_df["hispanic"] == 1) & (node_df["worker"] == 1))
        hispanic_workers = sum((node_df["hispanic"] != 1) & (node_df["worker"] == 1))
        non_workers_any = sum(node_df["worker"] == 0)
        block = node_df['block_group_id'].iloc[0] # i think this is ok for now because they should all be the same
        node_id_list.append(node_id)

        row = [nhwhite_workers, nhblack_workers, nhasian_workers, hispanic_workers, non_workers_any, block]
        node_df_lol.append(row)
        
    workers_by_node = pd.DataFrame(node_df_lol, columns=["nhwhite_workers", "nhblack_workers","nhasian_workers",
            "hispanic_workers", "non_workers_any", "block_group"], index=node_id_list)
    
    
    return workers_by_node


beam_network_links = pd.read_csv('beam-network-links.csv')
beam_network_nodes = pd.read_csv('beam-network-nodes.csv')

net=pdna.Network(beam_network_nodes.x, beam_network_nodes.y, beam_network_links["from"], beam_network_links["to"],
                 beam_network_links[["travelTime"]])
net.precompute(10000)

def get_job_accessibilities(net, year, dist):
    '''returns the number of jobs within a radius of dist of each node'''
    df = get_job_locations(year)
    workers_df = get_workers_by_race(year)
    node_ids = df["node_id"]
    n = net.set(node_ids)
    s = net.aggregate(dist, type="sum", decay="linear")
    access = pd.DataFrame(s)
    access = access.rename({0:"jobs"}, inplace=False, axis=1)
    access = pd.merge(workers_df, access, right_index=True, left_index=True)
    return access
        
#an intermediate step to save data just in case
# get_job_accessibilities(net, 2025, 10000).to_csv('indicators_output/accessibilities_2025_1000.csv', index=False)
# get_job_accessibilities(net, 2015, 10000).to_csv('indicators_output/accessibilities_2015_1000.csv', index=False)
# get_job_accessibilities(net, 2010, 10000).to_csv('indicators_output/accessibilities_2010_1000.csv', index=False)

def group_access_by_geo(job_access_df):
    people_per_geo = sum(job_access_df["nhwhite_workers"] + job_access_df["nhblack_workers"]+job_access_df["nhasian_workers"]+job_access_df["hispanic_workers"])+1e-6
    node_access_nhw = sum(job_access_df["nhwhite_workers"]*job_access_df["jobs"])/people_per_geo
    node_access_nhb = sum(job_access_df["nhblack_workers"]*job_access_df["jobs"])/people_per_geo
    node_access_nha = sum(job_access_df["nhasian_workers"]*job_access_df["jobs"])/people_per_geo
    node_access_h = sum(job_access_df["hispanic_workers"]*job_access_df["jobs"])/people_per_geo

    return pd.Series(node_access_nhw, node_access_nhb, node_access_nha, node_access_h)

def accessibilities_by_race(job_accessibilities_df, year, dist, net, geography): 
    '''This is the the essence of the computation being performed to get the race-based accessibilities. This function
    takes in the year, buffer distance, pandana network (should be precomputed) and desired geography (right now this
    notebook has shapefiles set up for census tract ("census_tract") and block group ("block_group"). Returns a table indexed by 
    the id of the geography, and a column for each weighted accessibility by race.'''
    
    

    if geography == 'node':
        access_by_race_df = pd.DataFrame()
        people_per_geo = job_accessibilities_df["nhwhite_workers"] + job_accessibilities_df["nhblack_workers"]+job_accessibilities_df["nhasian_workers"]+job_accessibilities_df["hispanic_workers"]+1e-6
        node_access_nhw = job_accessibilities_df["nhwhite_workers"]*job_accessibilities_df["jobs"]/people_per_geo
        node_access_nhb = job_accessibilities_df["nhblack_workers"]*job_accessibilities_df["jobs"]/people_per_geo
        node_access_nha = job_accessibilities_df["nhasian_workers"]*job_accessibilities_df["jobs"]/people_per_geo
        node_access_h = job_accessibilities_df["hispanic_workers"]*job_accessibilities_df["jobs"]/people_per_geo
        
        access_by_race_df["node_access_nhw"] = node_access_nhw
        access_by_race_df["node_access_nhb"] = node_access_nhb
        access_by_race_df["node_access_nha"] = node_access_nha
        access_by_race_df["node_access_h"] = node_access_h
        return access_by_race_df
    else:
        import pdb; pdb.set_trace()
        access_geo = job_accessibilities_df.groupby(geography).agg(group_access_by_geo)
        access_geo.columns = ["node_access_nhw", "node_access_nhb", "node_access_nha", "node_access_h"]
        # job_access_df_lol = []
        # geo_id_list = []
        # for geo, job_access_df in job_accessibilities_df.groupby(geography):
        #     people_per_geo = sum(job_access_df["nhwhite_workers"] + job_access_df["nhblack_workers"]+job_access_df["nhasian_workers"]+job_access_df["hispanic_workers"])+1e-6
        #     node_access_nhw = sum(job_access_df["nhwhite_workers"]*job_access_df["jobs"])/people_per_geo
        #     node_access_nhb = sum(job_access_df["nhblack_workers"]*job_access_df["jobs"])/people_per_geo
        #     node_access_nha = sum(job_access_df["nhasian_workers"]*job_access_df["jobs"])/people_per_geo
        #     node_access_h = sum(job_access_df["hispanic_workers"]*job_access_df["jobs"])/people_per_geo
        #     geo_id_list.append(geo)
        #     row = [node_access_nhw, node_access_nhb, node_access_nha, node_access_h]
        #     job_access_df_lol.append(row)
            
        # access_geo = pd.DataFrame(job_access_df_lol, columns=["access_nhwhite", "access_nhblack","access_nhasian",
        #           "access_hispanic"], index=geo_id_list)
    
    
        return access_geo

bay_county_codes = ['001', '013', '097', '095', '081', '085', '075', '041', '055'] 
block_groups = gp.read_file(shapefiles_path+'tl_2018_06_bg/tl_2018_06_bg.shp')
bay_bg = block_groups[(block_groups["COUNTYFP"].isin(bay_county_codes)) & (block_groups["ALAND"]> 100)]

tracts = gp.read_file(shapefiles_path+'tl_2018_06_tract/tl_2018_06_tract.shp')
bay_tracts = tracts[(tracts["COUNTYFP"].isin(bay_county_codes)) & (tracts["ALAND"]> 100)]

def get_access_by_race_geo(year, dist, net, geographies):
    '''merge the relevant shapefiles with the race weighted accessibilities tables to allow mapping. geographies is a list of 
    desired geographies'''
    access_by_geos = {}
    job_accessibilities_df = get_job_accessibilities(net, year, dist)

    
    for geography in geographies:
        job_access_by_race_df = accessibilities_by_race(job_accessibilities_df, year, dist, net, geography)
        if (geography == 'node'):
            access_by_geo = job_access_by_race_df
        elif (geography == 'census_tract'):
            access_by_geo = pd.merge(bay_tracts, job_access_by_race_df, right_index=True, left_on='GEOID')
        elif (geography == 'block_group'):
            access_by_geo = pd.merge(bay_bg, job_access_by_race_df, right_index=True, left_on='GEOID')

        access_by_geos[geography] = access_by_geo
    return access_by_geos

    
##add the final access tables

access_10000_2025 = get_access_by_race_geo(2025, 10000, net, ["census_tract", "block_group", "node"])
for geo, df in access_10000_2025.items():
    df.to_csv("indicators_output/access_10000_2025_{0}.csv".format(geo))

access_10000_2015 = get_access_by_race_geo(2015, 10000, net, ["census_tract", "block_group", "node"])
for geo, df in access_10000_2015.items():
    df.to_csv("indicators_output/access_10000_2015_{0}.csv".format(geo))

access_10000_2010 = get_access_by_race_geo(2010, 10000, net, ["census_tract", "block_group", "node"])
for geo, df in access_10000_2010.items():
    df.to_csv("indicators_output/access_10000_2010_{0}.csv".format(geo))


















