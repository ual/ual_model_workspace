import numpy as np
import pandas as pd
import pandana as pdna
import geopandas as gp

homedata_file_path = '/home/data/'
dd = '/home/data/spring_2019/base/'
shapefiles_path = '/home/simon/spatial-data/'
model_outputs_path = '/home/data/spring_2019/outputs/'

counties = {"Contra_Costa": "13", "Alameda": "1", "San_Mateo": "81", "Santa_Clara": "85", "Solano": "95",
    "Sonoma": "97", "Marin": "41", "San_Francisco": "75", "Napa": "55"}

counties_int = {"Contra_Costa": 13, "Alameda": 1, "San_Mateo": 81, "Santa_Clara": 85, "Solano": 95,
    "Sonoma": 97, "Marin": 41, "San_Francisco": 75, "Napa": 55}

demographic_cats = ['income_1st', 'income_2nd', 'income_3rd', 'income_4th', 'nhwhite_workers', 
     'nhblack_workers', 'nhasian_workers', 'hispanic_workers', 'edu_lessthanhs', 'edu_hs_ged', 'edu_assoc', 
                    'edu_bach','edu_grad', 'own', 'rent']

def get_data():
    # '''gets all relevant tables from the HDF5 and saves them to a dictionary that is indexed by 1) year and 
    # 2) table name. Closes the store. The function is assigned to the global variable data_dict'''
    data_dict = {}
    hdfstore = pd.HDFStore(model_outputs_path+'model_data_output.h5', mode='r') #sometimes doesnt work with a relative file path
    for year in [2010, 2015, 2025]:
        persons = hdfstore["/{}/persons".format(year)].sample(100000)
        hh = hdfstore["/{}/households".format(year)].sample(100000)
        buildings = hdfstore["/{}/buildings".format(year)].sample(100000)
        parcels = hdfstore["/{}/parcels".format(year)].sample(100000)
        jobs = hdfstore["/{}/jobs".format(year)].sample(100000)
        data_dict[year] = {"hh": hh, "buildings": buildings, "parcels": parcels, "jobs": jobs, "persons": persons}
   
    hdfstore.close()
    return data_dict
print("getting data")
data_dict = get_data()

beam_network_links = pd.read_csv('beam-network-links.csv')
beam_network_nodes = pd.read_csv('beam-network-nodes.csv')


net=pdna.Network(beam_network_nodes.x, beam_network_nodes.y, beam_network_links["from"], beam_network_links["to"],
                 beam_network_links[["travelTime"]])
net.precompute(10000)
del beam_network_links
del beam_network_nodes
print("precomputed network")

def get_merged_data(year):
    '''merges the household and buildings and parcels and persons tables together in an inner merge, 
    resulting in a dataframe with every person, their household information and their geographic information
    like block group id and parcel id, and node id'''
        
    
    # try:
    buildings = data_dict[year]["buildings"].reset_index()[["building_id", "parcel_id"]]
    parcels = data_dict[year]["parcels"].reset_index()[["parcel_id", "county_id", "node_id"]]
    bldg_parc = pd.merge(buildings, parcels, on="parcel_id")
    hh = data_dict[year]["hh"]
    persons = data_dict[year]["persons"]
    # except Exception as e:
    #   print(e)
    
    
    
    hh_build = pd.merge(hh, bldg_parc, on="building_id")
    
    

    hh_build.index.name = "household_id"
    
    hh_build = hh_build.reset_index()
   
    persons = data_dict[year]["persons"]
    persons.index.name = "person_id"
    
    buildings_persons = pd.merge(persons, hh_build, on='household_id')
    
    
    buildings_persons["block_group_id"] = buildings_persons["block_group_id"].apply(lambda x: "0"+x)
    buildings_persons["census_tract"] = buildings_persons["block_group_id"].apply(lambda x: x[:-1])
    return buildings_persons

merged_2025 = get_merged_data(2025)


def get_job_locations(year):
    #     '''get the location of the jobs by merging the jobs table with the buildings table on building_id and that
    # table with the parcels table on parcel_id, resulting in each job being assigned to a node id to be used
    # in the pandana network'''
    
    buildings = data_dict[year]['buildings'].reset_index()[['building_id', 'parcel_id']]
    
    jobs = data_dict[year]['jobs'].reset_index()[['occupation_id', 'building_id', 'sector_id']]
    
    parcels = data_dict[year]['parcels'][['parcel_id_local', 'block_id', 'county_id', 'y', 'x', 'node_id']].reset_index()
    
    
    jobs_buildings = pd.merge(buildings, jobs, on='building_id')
    
    
    jobs_merge = pd.merge(jobs_buildings, parcels, on='parcel_id')
    jobs_merge['census_tract'] = jobs_merge['block_id'].apply(lambda x: x[:-4])
    jobs_merge['block_group'] = jobs_merge['block_id'].apply(lambda x: x[:-3])

    return jobs_merge

jobs_2025 = get_job_locations(2025)
print("getting job locations")


def get_job_accessibilities(net, year, dist):
    '''returns the number of jobs within a radius of dist of each node'''
    # df = get_job_locations(year)
    df = jobs_2025
    node_ids = df["node_id"]
    n = net.set(node_ids)
    s = net.aggregate(dist, type="sum", decay="linear")
    access = pd.DataFrame(s)
    access = access.rename({0:"jobs"}, inplace=False, axis=1)
    # access = pd.merge(workers_df, access, right_index=True, left_index=True)
    return access #number of jobs accessible within a given radius indexed by a node id

    

def get_hh_attributes(household_df): 
    '''to be used in a .apply function on the get merged data. counts the number of people in a certain demographic in the household'''

    income_1st = household_df["base_income_quartile"].iloc[0] == 1
    income_2nd = household_df["base_income_quartile"].iloc[0] == 2
    income_3rd = household_df["base_income_quartile"].iloc[0] == 3
    income_4th = household_df["base_income_quartile"].iloc[0] == 4

    renter = household_df["tenure"].iloc[0] == 'rent'
    owner = household_df["tenure"].iloc[0] == 'own' 

    # number of workers of each race in the household
    nhwhite_workers = sum((household_df["race_id"] == 1) & (household_df["hispanic"] == 1) & (household_df["worker"] == 1))
    nhblack_workers = sum((household_df["race_id"] == 2) & (household_df["hispanic"] == 1) & (household_df["worker"] == 1))
    nhasian_workers = sum((household_df["race_id"] == 6) & (household_df["hispanic"] == 1) & (household_df["worker"] == 1))
    hispanic_workers = sum((household_df["hispanic"] != 1) & (household_df["worker"] == 1))
    non_workers_any = sum(household_df["worker"] == 0)

    #number of household members of each education level
    edu_lessthanhs = sum(household_df["edu"] <= 15)
    edu_hs_ged = sum((household_df["edu"] == 16) & (household_df["edu"] == 17))
    edu_assoc =sum(household_df["edu"] == 20)
    edu_bach =sum(household_df["edu"] == 21)
    edu_grad =sum(household_df["edu"] > 21)

    census_tract = household_df["census_tract"].iloc[0]
    node_id = household_df["node_id"].iloc[0]
    county_id = household_df["county_id"].iloc[0]

    return pd.Series([income_1st, income_2nd, income_3rd, income_4th, nhwhite_workers, nhblack_workers, nhasian_workers, hispanic_workers, edu_lessthanhs, 
        edu_hs_ged, edu_assoc, edu_bach, edu_grad, renter, owner, census_tract, county_id, node_id])




def accessibilities_attributes(year, net, dist):
    # df = get_merged_data(year)
    df = merged_2025
    with_ed_ra_ten = df.groupby('household_id').apply(get_hh_attributes)
    print(len(with_ed_ra_ten))
    print(len(with_ed_ra_ten.columns))
    with_ed_ra_ten.columns = ['income_1st', 'income_2nd', 'income_3rd', 'income_4th', 'nhwhite_workers', 'nhblack_workers', 'nhasian_workers',
    'hispanic_workers', 'edu_lessthanhs', 'edu_hs_ged', 'edu_assoc', 'edu_bach', 'edu_grad', 'own', 'rent', 'census_tract', 'county_id', 'node_id']
    access = get_job_accessibilities(net, year, dist)
    attr_and_access = pd.merge(with_ed_ra_ten, access, right_index=True, left_on="node_id").reset_index()

    return attr_and_access


def get_geog_totals_by_demog(geog_df):
    '''returns a dictionary with keys of charactatistics and values as regional totals of the people/households fitting that charactaristic'''
    # households_with_attributes = accessibilities_attributes(year, net, dist)
    
    characteristic_totals = {}
    for col in demographic_cats:
#         display(geog_df.head())
        characteristic_totals[col] = len(geog_df[geog_df[col] > 0])
    return characteristic_totals

def get_jobs_demog_product(node_df, geog_df = None):
    '''get the average access by demographic group per node, to be summed up at the region and county level for different time periods and divided by the number of 
    people in that demographic group at that region. node_df is the whole table of nodes if it is calculated at the regional level, and it is just the portion 
    of the node_df that fits the given county if it should be aggregated at the county level'''
    
    denom = get_geog_totals_by_demog(geog_df)
        
    avgs = []
    for cat in demographic_cats:

        avgs.append((sum(node_df[cat])*(node_df["jobs"].iloc[0]))/(denom[cat]+1e-6))
    print("length of get_jobs_demog_product_ avg array", len(avgs))
    return pd.Series(avgs)


# get_jobs_demog_product(accessibilities_attributes(2025, net, 2000), '1')
 
def accessibilities_by_demog(year, dist, net, geog_id):
    '''take the mean accessibility of jobs for people of a certain demographic based on
        a given geography.'''
    attr = accessibilities_attributes(year, net, dist)
    if (geog_id == 'region'):
        geog_df = attr
        
    elif (geog_id in counties_int.values()):
#         print("this is a county ", geog_id)
        geog_df = attr[attr["county_id"] == geog_id]     
    else:
        raise ValueError
    final_avg_access = geog_df.groupby('node_id').apply(get_jobs_demog_product, geog_df = geog_df)
    print("final avg access df length", len(final_avg_access))
    final_avg_access.columns = ['q1_avg_access','q2_avg_access','q3_avg_access','q4_avg_access','rent_avg_access','own_avg_access',
    'white_avg_access','black_avg_access','asian_avg_access','hisp_avg_access', "lessthanhs_avg_access", "hs_ged_avg_access", 
    "assoc_avg_access", "bach_avg_access", "grad_avg_access"]
    return final_avg_access



    


# accessibilities_by_demog(2025, 5000, net, 'region').sum(axis=0).to_csv("indicators_output/region_5000_2025")
# print("finished region")
# accessibilities_by_demog(2025, 5000, net, 1).sum(axis=0).to_csv("indicators_output/alameda_5000_2025")
# print("finished 1")
# accessibilities_by_demog(2025, 5000, net, 41).sum(axis=0).to_csv("indicators_output/marin_5000_2025")
# print("finished 41")
accessibilities_by_demog(2025, 5000, net, 13).sum(axis=0).to_csv("indicators_output/marin_5000_2025")
print("finished 13")
accessibilities_by_demog(2025, 5000, net, 81).sum(axis=0).to_csv("indicators_output/marin_5000_2025")
print("finished 81")
accessibilities_by_demog(2025, 5000, net, 85).sum(axis=0).to_csv("indicators_output/marin_5000_2025")
print("finished 85")
# accessibilities_by_demog(2025, 10000, net, 75).sum(axis=0).to_csv("indicators_output/marin_10000_2025")
# accessibilities_by_demog(2025, 10000, net, 55).sum(axis=0).to_csv("indicators_output/marin_10000_2025")
# accessibilities_by_demog(2025, 10000, net, 97).sum(axis=0).to_csv("indicators_output/marin_10000_2025")
# accessibilities_by_demog(2025, 10000, net, 95).sum(axis=0).to_csv("indicators_output/marin_10000_2025")






# bay_county_codes = ['001', '013', '097', '095', '081', '085', '075', '041', '055'] 
# block_groups = gp.read_file(shapefiles_path+'tl_2018_06_bg/tl_2018_06_bg.shp')
# bay_bg = block_groups[(block_groups["COUNTYFP"].isin(bay_county_codes)) & (block_groups["ALAND"]> 100)]
# del block_groups

# tracts = gp.read_file(shapefiles_path+'tl_2018_06_tract/tl_2018_06_tract.shp')
# bay_tracts = tracts[(tracts["COUNTYFP"].isin(bay_county_codes)) & (tracts["ALAND"]> 100)]
# del tracts


# def get_access_by_demog_geo(year, dist, net, geographies):
# #     '''merge the relevant shapefiles with the race weighted accessibilities tables to allow mapping. geographies is a list of 
# #     desired geographies'''
#     access_by_geos = {}
#     for geography in geographies:
#         assert geography in ['node_id', 'census_tract']
#         job_access_by_demog_df = accessibilities_by_demog(year, dist, net, geography)
#         if (geography == 'node_id'):
#             access_by_geo = pd.merge(beam_network_nodes, job_access_by_demog_df, right_index=True, left_on='id')
#         elif (geography == 'census_tract'):
#             access_by_geo = pd.merge(bay_tracts, job_access_by_demog_df, right_index=True, left_on='GEOID')
#         access_by_geos[geography] = access_by_geo
#     return access_by_geos



   












