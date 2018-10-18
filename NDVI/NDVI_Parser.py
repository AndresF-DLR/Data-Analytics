"""
@author: AndresF-DLR

The "Canadian Urban Environmental Health Research Consortium" holds yearly NDVI scores for each postal code in the GTA
from 1987 to 2015. The data is transferred in two ways: postal codes are shared within one repository of csv files, each file
holds a year's records for its extant postal codes; NDVI scores are forwarded as three file repositories (NDVI mean, NDVI max, and
NDVI growing season mean) each holding a list of csv files (one for each year's scores in one of the aforementioned categories).

This script cleans and aggregates the data into a list of csv files (one per year) that includes NDVI scores from the files mentioned
above while dropping data that is irrelevant to geospatial analysis. 
"""

import os
import pandas as pd
import numpy as np

path = os.getcwd()

def getPostCodes():
    """
    Input: folder repository holding different csv records for each year's existing postal codes in the GTA.
    Output: dictionary holding one dataframe of cleaned postal code data (postal code, longitude and latitude) per year
    Schema: dict = {<year>: <dataframe>,...} 
    """
    
    os.chdir("POSTALCODES/DMTI_SLI")
    
    pc_Years = {}
    
    for i in os.listdir():
        pc_year = i[-6:-4]

        year_Df = pd.read_csv(i, index_col=0)
        
        #Removes columns that are not necessary for the analysis or geo-coding process
        drop_Columns = ['PROV_', 'BIRTH_DATE_', 'RET_DATE_', 
                              'DOM_DELMDE_', 'POC_BUS_', 'POC_HOUSE_', 
                              'POC_FARM_', 'POSITION_','MULTI_ST_']
        drop_Columns = list(map(lambda x: x + pc_year, drop_Columns))
        
        year_Df = year_Df.drop(columns= drop_Columns)
    
        pc_Years[pc_year] = year_Df
    
    os.chdir(path)
    
    return pc_Years

def addData(pc_dict):
    """
    Inputs: postal code dictionary; folder repositories for NDVI mean, maximum, and growing season data
    Output: extended postal code dictionary, now with each postal code's yearly NDVI mean, yearly
             NVDI maximum, and growing season NVDI mean.
    Note: script removes null, invalid or 0 data entries with the respective mean for a larger area of study.
    """
    
    data_Path = path + "/DATASETS_ANNUAL/GREEN/LAN"
    
    os.chdir(data_Path)
    
    for cat in os.listdir():
        
        os.chdir(cat)
        
        for file in os.listdir():
            
            
            data_year = file[-6:-4]
            
            year_Df = pd.read_csv(file, index_col=0)
            
            #Replace attributes showing insufficient data with the mean value for a greater area of study
            year_Df[year_Df.columns[0]] = year_Df.replace({-9999:np.nan, -1:np.nan})
            
            year_Df[year_Df.columns[0]] = np.where(year_Df[year_Df.columns[0]].isnull(), year_Df[year_Df.columns[1]], year_Df[year_Df.columns[0]])
            
            year_Df = year_Df.drop(columns=year_Df.columns[1:])
            
            new_Column_Name = "MEAN_" + cat +"_"+data_year
            
            year_Df = year_Df.rename(columns={year_Df.columns[0]: new_Column_Name})
            
            try:
                result = pd.concat([pc_dict[data_year], year_Df], axis=1, join='inner')
                pc_dict[data_year] = result
                
            except KeyError:
                pass 
            
        os.chdir(data_Path)
        
    os.chdir(path)

def createCSVs(pc_dict):
    """
    Input: postal code dictionary file with aggregated yearly NDVI data. 
    Output: one .csv file for each postal code year file. 
    """
    os.chdir("AGGREGATED_DATA")
    
    for df in pc_dict:
        file_name = df + "_pc_data.csv"
        pc_dict[df].to_csv(file_name)
        print("Done with " + df)
        
