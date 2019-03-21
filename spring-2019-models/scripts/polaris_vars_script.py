import pandas as pd
import numpy as np
import time
import geopandas as gp
import os
import tables
import orca
from synthpop.census_helpers import Census


filepath = "/home/amelia/ual_model_workspace/spring-2019-models/notebooks-amelia/"

#Get PUMS data for Illinois
c = Census('181ed8c64531c167176365d52ac460d969d54cf2')
pop = c.download_population_pums('17')
pums_relevant = pop[["serialno", 'SCHL', 'HISP', "MIL", "ESR"]]
print("getting pums..")

#get urbansim tables
store = pd.HDFStore('/home/amelia/ual_model_workspace/model_data.h5') #sometimes doesnt work with a relative file path
households = store['households']
households.index.name = 'household_id'
households_reset = households.reset_index()
households_reset["block_id"] = households_reset["block_id"].astype(str)
households_reset["block_id"] = households_reset["block_id"].str[:12] #take the first 11 digits of the FIPS to get the block group

persons = store["persons"]
persons.index.name = 'person_id'
persons_reset = persons.reset_index()

jobs = store["jobs"]
jobs_reset = jobs.reset_index()
jobs_reset["block_id"] = jobs_reset["block_id"].astype(str)
jobs_reset["block_id"] = jobs_reset["block_id"].str[:12] #take the first 11 digits of the FIPS to get the block group

households_pums_merge = pd.merge(pums_relevant, households_reset, on='serialno') #merge relevant vars in the PUMS data with the urbansim households data
hh_person_pums = pd.merge(households_pums_merge, persons_reset, on='household_id') #merge the resulting table with the urbansim persons table by household id

#popsyn marginals
def education(df): #takes in the combined pums, household, persons table
    EDUC_LESSHS_EMPLOYED = sum((df["edu"] <= 15) & ((df["ESR"] == 1) | (df["ESR"] == 2) | (df["ESR"] == 4) | (df["ESR"] == 5)))
    EDUC_LESSHS_UNEMPLOYED = sum((df["edu"] <= 15) & (df["ESR"] == 3))
    EDUC_LESSHS_NILF = sum((df["edu"] <= 15) & (df["ESR"] == 6))
    
    #HS = high school diploma (16) or GED (17)
    EDUC_HS_EMPLOYED = sum(((df["edu"] == 16) | (df["edu"] == 17)) & ((df["ESR"] == 1) | (df["ESR"] == 2) | (df["ESR"] == 4) | (df["ESR"] == 5)))
    EDUC_HS_UNEMPLOYED = sum((df["edu"] == 16) | (df["edu"] == 17) & (df["ESR"] == 3))
    EDUC_HS_NILF = sum((df["edu"] == 16) | (df["edu"] == 17) & (df["ESR"] == 6))
    
    #SOMECOLLEGE = less than 1 year of college, no degree (18) more than 1 yr, no degree (19)
    EDUC_SOMECOLLEGE_EMPLOYED = sum(((df["edu"] == 18) | (df["edu"] == 19)) & ((df["ESR"] == 1) | (df["ESR"] == 2) | (df["ESR"] == 4)| (df["ESR"] == 5)))
    EDUC_SOMECOLLEGE_UNEMPLOYED = sum(((df["edu"] == 18) | (df["edu"] == 19)) & (df["ESR"] == 3))
    EDUC_SOMECOLLEGE_NILF = sum(((df["edu"] == 18) | (df["edu"] == 19)) & (df["ESR"] == 6))
                               
  
    #COLLEGE = associates (20), bachelors (21), masters (22), professional (23), doctorate (24)
    EDUC_COLLEGE_EMPLOYED = sum(((df["edu"] >= 20) & (df["edu"] <= 24)) & ((df["ESR"] == 1) | (df["ESR"] == 2) | (df["ESR"] == 4)| (df["ESR"] == 5)))
    EDUC_COLLEGE_UNEMPLOYED = sum(((df["edu"] >= 20) & (df["edu"] <= 24)) & (df["ESR"] == 3))  
    EDUC_COLLEGE_NILF  = sum(((df["edu"] >= 20) & (df["edu"] <= 24)) & (df["ESR"] == 6))
    EDUC_UNDER25 = sum(df["age"] < 25)
    EDUC_65PLUS = sum(df["age"] >=65)
                           
                          
    return [EDUC_LESSHS_EMPLOYED,EDUC_LESSHS_UNEMPLOYED,EDUC_LESSHS_NILF,EDUC_HS_EMPLOYED,EDUC_HS_UNEMPLOYED,
    EDUC_HS_NILF,EDUC_SOMECOLLEGE_EMPLOYED,EDUC_SOMECOLLEGE_UNEMPLOYED,EDUC_SOMECOLLEGE_NILF,EDUC_COLLEGE_EMPLOYED,
    EDUC_COLLEGE_UNEMPLOYED,EDUC_COLLEGE_NILF,EDUC_UNDER25,EDUC_65PLUS]


def sort_incomes(df):
    HHINC_LESS20K = sum(df["income"] < 20000)
    HHINC_20TO35K = sum((df["income"] > 20000) & (df["income"] <= 35000))
    HHINC_35TO50K = sum((df["income"] > 35000) & (df["income"] <= 50000))
    HHINC_50TO75k = sum((df["income"] > 50000) & (df["income"] <= 75000))
    HHINC_75TO100K = sum((df["income"] > 75000) & (df["income"] <= 100000))
    HHINC_100TO150K = sum((df["income"] > 100000) & (df["income"] <= 150000))
    HHINC_OVER150K = sum(df["income"] >= 150000)
    return [HHINC_LESS20K, HHINC_20TO35K,HHINC_35TO50K,HHINC_50TO75k, HHINC_75TO100K,
           HHINC_100TO150K, HHINC_OVER150K]


def hh_size(df):
    HHSIZE_1 = sum(df["persons"] == 1)
    HHSIZE_2 = sum(df["persons"] == 2)
    HHSIZE_3 = sum(df["persons"] == 3)
    HHSIZE_4 = sum(df["persons"] == 4)
    HHSIZE_5 = sum(df["persons"] == 5)
    HHSIZE_6 = sum(df["persons"] == 6)
    HHSIZE_7 = sum(df["persons"] == 7)
    return [HHSIZE_1,HHSIZE_2,HHSIZE_3,HHSIZE_4,HHSIZE_5,HHSIZE_6,HHSIZE_7]


def num_vehicles(df):
    NVEH_0 = sum(df["cars"] == 0)
    NVEH1 = sum(df["cars"] == 1)
    NVEH2 = sum(df["cars"] == 2)
    NVEH_3 = sum(df["cars"] >= 3)
    return [NVEH_0, NVEH1, NVEH2, NVEH_3]

def gender(df):
    SEX_MALE = len(df[df["sex"] == 1])
    SEX_FEMALE = len(df[df["sex"] == 2])
    return [SEX_MALE, SEX_FEMALE]

def age(df):
    AGE_under15 = sum(df["age"] < 15)  
    AGE_15to24 = sum((df["age"] <= 24) & (df["age"] > 15))
    AGE_25to34 = sum((df["age"] <= 34) & (df["age"] > 25))
    AGE_35to44 = sum(df["age"] <= 44 & (df["age"] > 35))
    AGE_45to54 = sum(df["age"] <= 54 & (df["age"] > 45))
    AGE_55to64 = sum(df["age"] <= 64 & (df["age"] > 55))
    AGE_65plus = sum(df["age"] >=65)
    return [AGE_under15, AGE_15to24, AGE_25to34, AGE_35to44, AGE_45to54, AGE_55to64, AGE_65plus]

def race(df): #now takes in combined persons, households, pums dataframe
    RACE_WHITE = len(df[(df["race_id"] == 1) & (df["HISP"] == 1)]) # 1 is non hispnic
    RACE_BLACK = len(df[(df["race_id"] == 2) & (df["HISP"] == 1)])
    RACE_INDIAN = len(df[(df["race_id"] == 3) & (df["HISP"] == 1)])
    RACE_ASIAN = len(df[(df["race_id"] == 6) & (df["HISP"] == 1)])
    RACE_OTHER = len(df[(df["race_id"] == 8) & (df["HISP"] == 1)])  
    RACE_HISPANIC = len(df[((df["race_id"] == 1)|(df["race_id"] == 2)|(df["race_id"] == 3)|(df["race_id"] == 4)| (df["race_id"] == 6) | (df["race_id"] == 8)) & (df["HISP"] != 1)]) 
    return [RACE_WHITE, RACE_BLACK, RACE_INDIAN, RACE_ASIAN, RACE_OTHER, RACE_HISPANIC]


def hhtype(df):
    owner = sum(df["tenure"] == 1) > 0 #tenure code 1 is owner, 2 is renter 
    spouse = sum(df["relate"] == 1) > 0 #if there is at least one person who is a husband or a wife
    HHT_OWN_MARRIED = np.count_nonzero((sum(df["tenure"] == 1)> 0) & (sum(df["relate"] == 1) > 0))
    HHT_OWN_NONFAMILY_SINGLE = sum((df["persons"] == 1) & (not spouse) & owner) # one person, no spouses, owner
    HHT_OWN_NONFAMILY_NOTALONE = sum((df["persons"] > 1) & (not spouse) & owner)# >one person, no spouses, owner
    HHT_RENT_MARRIED = np.count_nonzero((sum(df["tenure"] == 0)> 0) & (sum(df["relate"] == 1) > 0))
    HHT_RENT_NONFAMILY_SINGLE  = (not owner) & sum(df["persons"] == 1)# one person, at least one spouse, renter
    HHT_RENT_NONFAMILY_NOTALONE = (not owner) & sum(df["persons"] > 1)# >one person, at least one spouse, renter
    return [HHT_OWN_MARRIED, HHT_RENT_MARRIED, HHT_OWN_NONFAMILY_NOTALONE, HHT_OWN_NONFAMILY_SINGLE, 
            HHT_RENT_NONFAMILY_SINGLE, HHT_RENT_NONFAMILY_NOTALONE]
    print("about to start popsyn groupby")
start = time.time()
df_lol = []
blk_id_list = []
for blk_id, blk_df in hh_person_pums.groupby("block_id"):
    blk_id_list.append(blk_id)
    row = []
    row.extend(gender(blk_df))
    row.extend(race(blk_df))
    row.extend(age(blk_df))  
    row.extend(education(blk_df))
    row.extend(hhtype(blk_df))
    row.extend(sort_incomes(blk_df)) # returns list with counts of households in each income bin
    row.extend(hh_size(blk_df))
    row.extend(num_vehicles(blk_df))
    row.extend([len(blk_df)])
    df_lol.append(row)
popsyn_df = pd.DataFrame(df_lol, columns=["SEX_MALE", "SEX_FEMALE","RACE_WHITE",
             "RACE_BLACK", "RACE_INDIAN", "RACE_ASIAN", "RACE_OTHER", "RACE_HISPANIC", "AGE_under15", "AGE_15to24", "AGE_25to34", 
            "AGE_35to44", "AGE_45to54","AGE_55to64","AGE_65plus", "EDUC_LESSHS_EMPLOYED","EDUC_LESSHS_UNEMPLOYED","EDUC_LESSHS_NILF","EDUC_HS_EMPLOYED","EDUC_HS_UNEMPLOYED",
    "EDUC_HS_NILF","EDUC_SOMECOLLEGE_EMPLOYED","EDUC_SOMECOLLEGE_UNEMPLOYED","EDUC_SOMECOLLEGE_NILF","EDUC_COLLEGE_EMPLOYED",
    "EDUC_COLLEGE_UNEMPLOYED","EDUC_COLLEGE_NILF","EDUC_UNDER25","EDUC_65PLUS", "HHT_OWN_MARRIED", "HHT_RENT_MARRIED", "HHT_OWN_NONFAMILY_NOTALONE", 
                "HHT_OWN_NONFAMILY_SINGLE", "HHT_RENT_NONFAMILY_SINGLE", "HHT_RENT_NONFAMILY_NOTALONE","HHINC_LESS20K", "HHINC_20TO35K", "HHINC_35TO50K", 
        "HHINC_50TO75k", "HHINC_75TO100K", "HHINC_100TO150K", "HHINC_OVER150K", "HHSIZE_1", "HHSIZE_2",
        "HHSIZE_3", "HHSIZE_4", "HHSIZE_5", "HHSIZE_6", "HHSIZE_7",
        "NVEH_0", "NVEH1", "NVEH2", "NVEH_3", "pop households"], index=blk_id_list)
end = time.time()
elapsed = end- start
elapsed

#write this dataframe to a popsyn marginals file
popsyn_marginals = popsyn_df.to_csv(filepath+'popsyn_marginals.csv') #this wasn't run last night
print("write popsyn marginals file")

#employment categories

def jobs_naics(df): #take in jobs df
    AGRICULTURE = len(df[df["sector_id"] == 11])
    MINING = len(df[df["sector_id"] == 21])
    UTILITIES = len(df[df["sector_id"] == 22])
    CONSTRUCTION = len(df[df["sector_id"] == 23])
    MANUFACTURING = len(df[(df["sector_id"] >= 31) & (df["sector_id"] <= 33)])
    WHOLESALE = len(df[df["sector_id"] == 42])
    RETAIL = len(df[(df["sector_id"] == 44) | (df["sector_id"] == 45)])
    TRANSPORTATION = len(df[(df["sector_id"] == 48) | (df["sector_id"] == 49)])
    INFORMATION = len(df[df["sector_id"] == 51])
    FINANCE = len(df[df["sector_id"] == 52])
    REALESTATE = len(df[df["sector_id"] == 53])
    PROFESSIONAL = len(df[df["sector_id"] == 54])
    EDUCATION = len(df[df["sector_id"] == 61])
    MEDICAL_SOCIALWORK = len(df[df["sector_id"] == 62])
    ENTERTAINMENT = len(df[df["sector_id"] == 71])
    SERVICES = len(df[df["sector_id"] == 81])
    ADMINISTRATION = len(df[df["sector_id"] == 92])
    return [AGRICULTURE, MINING, UTILITIES, CONSTRUCTION, MANUFACTURING, WHOLESALE, RETAIL, TRANSPORTATION,
        INFORMATION, FINANCE, REALESTATE, PROFESSIONAL, EDUCATION, MEDICAL_SOCIALWORK, ENTERTAINMENT, SERVICES, ADMINISTRATION]


def other_job_vars(df): #take in puma df
#unemployed and military counts
    MILITARY = sum((df["MIL"] != 4) | (df["MIL"] != np.float64(np.nan))) #1 is active duty, 2 is past active duty, 3 is reserves and training, 4 is never served
    UNEMPLOYED = sum((df["ESR"] == float(3.0)))
    return [MILITARY, UNEMPLOYED]
        
        
df_lol_jobs = []
blk_ids_jobs = []
for blk_id_j, df in jobs_reset.groupby("block_id"):
    blk_ids_jobs.append(blk_id_j)
    row = []
    row.extend(jobs_naics(df))
    df_lol_jobs.append(row)
jobs_df1 = pd.DataFrame(df_lol_jobs, columns=["AGRICULTURE", "MINING", "UTILITIES", "CONSTRUCTION", "MANUFACTURING", 
    "WHOLESALE", "RETAIL", "TRANSPORTATION", "INFORMATION", "FINANCE", "REALESTATE", "PROFESSIONAL", 
    "EDUCATION", "MEDICAL_SOCIALWORK", "ENTERTAINMENT", "SERVICE", "ADMINISTRATION"], index = blk_ids_jobs)


df_lol_other_jobs = []
blk_ids_other_jobs = []
for blk_id_oj, oj_df in hh_person_pums.groupby("block_id"):
    blk_ids_other_jobs.append(blk_id_oj)
    row = []
    row.extend(other_job_vars(oj_df))
    df_lol_other_jobs.append(row)
jobs_df2 = pd.DataFrame(df_lol_other_jobs, columns=["MILITARY", "UNEMPLOYED"], index = blk_ids_other_jobs)

jobs_file = pd.merge(jobs_df1, jobs_df2, right_index=True, left_index=True) #merge the two employment categorie dfs together

jobs_file.to_csv(filepath+ "employment_categories.csv") #write it to a csv
print("write employment file")

#TAZ land use vars
blk_grp_shpfile = gp.read_file(filepath+"tl_2017_17_bg/tl_2017_17_bg.shp")
land_area = blk_grp_shpfile[["GEOID", "ALAND"]]
land_area["GEOID"] = land_area["GEOID"].astype(str)

land_use = pd.read_csv(filepath + 'Chicago_block_LandUse.csv') #land use file is at the block level, we want the block group level
land_use["GEOID"] = land_use["GEOID"].astype(str)
land_use["GEOID"] = land_use["GEOID"].str[:12] #take the first 11 digits of the FIPS to get the block group
land_use.drop(['Unnamed: 0','Unnamed: 2', 'propAreaCheck'], axis=1, inplace=True)
land_use_area = pd.merge(land_use, land_area, how='inner', left_on='GEOID', right_on='GEOID')

lu_types = ['L1111', 'L1112', 'L1130', 'L1140', 'L1151', 'L1211', 'L1212',
       'L1214', 'L1215', 'L1216', 'L1220', 'L1240', 'L1250', 'L1310', 'L1321',
       'L1322', 'L1330', 'L1340', 'L1350', 'L1360', 'L1370', 'L1380', 'L1410',
       'L1420', 'L1431', 'L1432', 'L1433', 'L1450', 'L1511', 'L1512', 'L1520',
       'L1530', 'L1540', 'L1550', 'L1561', 'L1562', 'L1563', 'L1564', 'L1565',
       'L1570', 'L2000', 'L3100', 'L3200', 'L3300', 'L3400', 'L3500', 'L4110',
       'L4120', 'L4130', 'L4140', 'L4210', 'L4220', 'L4230', 'L4240', 'L5000',
       'L6100', 'L6200', 'L6300', 'L6400', 'L9999']
#2590000 square meters in a square mile

for lu in lu_types:
    classification = 'other_area'
    if (lu == 'L1240'):
        classification = "entertainment_area"
    elif (lu == 'L1400' or lu == 'L1410' or lu == 'L1420' or lu == 'L1430' or lu == 'L1431' or lu == 'L1432' 
          or lu == 'L1433' or lu == 'L1450'):
        classification = "industrial_area"
    elif (lu == 'L1220'):
        classification = "office_area"
    elif (lu == 'L1300' or lu == 'L1310' or lu == 'L1320' or lu == 'L1321' or lu == 'L1322' or
          lu == 'L1330' or lu == 'L1340' or lu == 'L1350' or lu == 'L1360' or lu == 'L1370' or lu == 'L1380'):
        classification = "institutional_area"
    elif (lu == 'L1100' or lu=='L1111' or lu == 'L1112' or lu == 'L1130' or lu == 'L1140' or lu == 'L1150'):
        classification = "residential_ area"
    elif (lu == 'L1210' or lu == 'L1211' or lu =='L1212' or lu =='L1214' or lu =='L1215' or lu =='L1216'):
        classification == "retail_area"
    elif (lu == 'L1321' or lu == 'L1322'):
        classification == 'school_area'
    land_use_area[classification+"Area_m2"] = (land_use_area["ALAND"]*land_use_area[lu]*2590000).astype(float)
    land_use_area.drop(lu,axis=1, inplace=True)

land_use_codes_sum = land_use_area.groupby(["GEOID"]).sum()

#misc summary stats for TAZ vars
def job_categories(df):
    employment_retail = len(df[(df["sector_id"] == 44) | (df["sector_id"] == 45)])
    employment_government = len(df[(df["sector_id"] == 92) | (df["sector_id"] == 61)]) # + military not yet included
    employment_manufacturing = len(df[(df["sector_id"] >= 31) & (df["sector_id"] <= 33)])
    employment_services = len(df[(df["sector_id"] == 81) | (df["sector_id"] == 62) | (df["sector_id"] == 71)])
    employment_industrial = len((df[(df["sector_id"] == 21)| (df["sector_id"] == 22) | (df["sector_id"] == 23)|
                (df["sector_id"] == 48) | (df["sector_id"] == 49)]))
    employment_other = len(df[~df["sector_id"].isin([11,44,45,92,61,31,32,33,81,62,71,21,22,23,48,49])])
    return [employment_retail, employment_government, employment_manufacturing, employment_services,
    employment_industrial, employment_other]


df_lol_employment = []
blk_ids_employment = []
for blk_id_e, df in jobs_reset.groupby("block_id"):
    blk_ids_employment.append(blk_id_e)
    row = []
    row.extend(job_categories(df))
    df_lol_employment.append(row)
employment_df = pd.DataFrame(df_lol_employment, columns=["employment_retail", "employment_government", "employment_manufacturing", "employment_services", 
            "employment_industrial", "employment_other"], index=blk_ids_employment)

def blk_wht_pct_gq(df):
    PCT_WHITE = len(df[df["race_id"] == 1])/len(df)
    PCT_BLACK = len(df[df["race_id"] == 2])/len(df)
    avg_income = np.mean(df["income"])
    group_quarters = len(df[df["member_id"] == 16])
    pop_households = len(df["household_id"].unique())
    return [PCT_WHITE, PCT_BLACK, avg_income, group_quarters, pop_households]


df_lol_persons = []
blk_id_list_persons = []
for blk_id_p, blk_df_p in hh_person_pums.groupby("block_id"):
    blk_id_list_persons.append(blk_id_p)
    row = []
    row.extend(blk_wht_pct_gq(blk_df_p))
    df_lol_persons.append(row)

    miscvars = pd.DataFrame(df_lol_persons, columns=["percent_white", "percent_black", "hh_inc_avg", "pop_group_quarters", "pop_households"], index=blk_id_list_persons)
    

# jobs_df, land_use_codes_sum, miscvars
landuse_employment = pd.merge(land_use_codes_sum, employment_df, how = "inner", left_index=True, right_index=True)
taz_file = pd.merge(landuse_employment, miscvars, left_index=True, right_index=True) 

taz_file.to_csv(filepath+'taz_landuse_variables.csv')#write TAZ land use file
print("write landuse file")









