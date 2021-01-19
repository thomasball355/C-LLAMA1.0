"""
C-LLAMA - Ball, T. 2021
This module was written right at the beginning of work on pyFALAFEL-WRAP as a
means to explore some of the data. It has since mutated into an initialising
module that takes the FBS data and splits it regionally. As such it is rather
full of junk code and mess that I intend to clean up at some point.
"""

import pandas as pd
import os
import pickle
import matplotlib.pyplot as plt
import scipy.stats as stat
import re
import numpy as np
from matplotlib import cm
from matplotlib import colors as mpl_col
import seaborn as sns

import lib.funcs.perc_contributions_WRAP as perc_contributions_WRAP
import lib.funcs.foodsupply_trajectory as foodsupply_trajectory
import lib.funcs.dat_io as io

import lib.dat.continents

    # current working directory, list of stuff in the directory
wd = os.getcwd() + "\\data"
list = os.listdir("./")

    # creates a colormap for plotting
def colormap_to_list(data, type, cmap):
    colors = []
    for k in range(0, len(data.index.get_level_values(f"{type}").to_list())):
        colors.append(mpl_col.to_hex(cmap(k/len(data.index.get_level_values(f"{type}").to_list()))))
    return colors

    # format x label, ticks, limits for 1961, 2013 (not very useful)
def x_format():
    plt.xlabel("Year")
    plt.xticks(np.arange(1965, 2015, 5))
    plt.xlim(1961, 2013)

    # easier way of saving data (ie without having to remember how to pickle)
def output_data(data, out_string, out_type, name):
    if out_type == "pickle":
        pickle.dump(data, open(f"{out_string}.obj", "wb"))
        print(f"Pickled \"{name}\" to \"{out_string}.obj\"")
    elif out_type == "pd_csv":
        data.to_csv(out_string+".csv")
        print(f"diet_contributionsved {name} as \"{out_string}\".csv")

    # makes directorys if they don't already exist (and subdirectories given by *args)
def dirs(directory, *args):
    string = f"{directory}\\"
    for arg in args:
        string += f"\\{arg}"
    if os.path.isdir(string) == False:
        os.makedirs(string)
        print(f"Made dir \"{string}\"")

    # takes continent level data (-antarctica) and splits each region into
    # subregions and saves as .obj and .csv
def data_produce(continent, area):
    FAO_country_metadata = pd.read_csv(f"{wd}\\FAOSTAT_data_10-16-2019_area_definitions.csv")
    group_list = []

    # produces a list of groups in the FAO data
    for item in FAO_country_metadata["Country Group"]:
        if item not in group_list:
            group_list.append(item)

    # returns list of countries in a region
    def region(metadata, region):
        data = metadata.loc[metadata["Country Group"] == region]
        return data

    # splits region into subregions to check if any countries are "left out"
    # eg. split Africa into Northern, Southern, Eastern, Western, Central. This leaves Zanzibar out ( :c )
    def regionfinder(area, *args):
        region_list = region(FAO_country_metadata, area)["Country"].to_list()
        rejectlist = []
        for country in region_list:
            accounted = False
            count = 0
            for arg in args:
                if country in region(FAO_country_metadata, arg)["Country"].to_list():
                    count += 1
                    accounted = True
            if count > 1:
                print(country)
            if accounted == False:
                rejectlist.append(country)
        print(rejectlist)

    # takes continent level data 'dataset' based on previously determined groups 'groups' and
    # splits each region into subregions and saves as .obj and .csv
    def data_make(dataset, groups):


        #["Area Code","Area","Item Code","Item","Element Code","Element","Unit"]
        try:
            data_in = pd.read_csv(f"{wd}\\FoodBalanceSheets_E_{dataset}_1.csv",encoding = "latin-1", index_col = ["Area","Item","Element","Unit", "Area Code", "Item Code", "Element Code"])
        except FileNotFoundError:
            try:
                data_in = pd.read_csv(f"{wd}\\{dataset}\\FoodBalanceSheets_E_{dataset}_1.csv",encoding = "latin-1", index_col = ["Area","Item","Element","Unit", "Area Code", "Item Code", "Element Code"])
            except FileNotFoundError:
                print(f"FoodBalanceSheets_E_{dataset}_1.csv not found in /data or /data/{dataset}, stopping...")

        # drop flags (for now, might need these later)
        data_in = data_in.drop(data_in.filter(regex = "Y....F").columns, axis = 1)

        for group in groups:
            g = group.replace(" ", "").replace("/", "").replace("(", "").replace(")", "").replace("-", "").upper()
            dirs(f"{wd}\\{dataset}", f"{g}")
            country_list = region(FAO_country_metadata, group)["Country"]
            data_out = data_in.iloc[data_in.index.get_level_values("Area").isin(country_list)]

            data_out = io.re_index_area(data_out)

            output_data(data_out, f"{wd}\\{dataset}\\{g}\\FoodBalanceSheets_E_{g}", "pd_csv", g)
            output_data(data_out, f"{wd}\\{dataset}\\{g}\\FoodBalanceSheets_E_{g}", "pickle", g)
    data_make(continent, area)

# split crop production
def crop_production_data(continent, region):

    try:
        data = pd.read_csv( f"data\\Production_Crops_E_{continent}_NOFLAG.csv",
                            encoding = "latin-1",
                            index_col = ["Area Code","Area","Item Code","Item","Element Code","Element","Unit"]).copy()
    except FileNotFoundError:
        try:
            data = pd.read_csv( f"data\\Production_Crops_E_{continent}_NOFLAG.csv",
                                encoding = "latin-1",
                                index_col = ["Area Code","Area","Item Code","Item","Element Code","Element","Unit"]).copy()
        except FileNotFoundError:
            print(f"\'Production_Crops_E_{continent}_NOFLAG.csv\' not found in /data or /data/{continent}, stopping...")

    regiondat = io.load(f"data\\{continent}\\{region}", f"FoodBalanceSheets_E_{region}").copy()
    data = data.reorder_levels([1,0,2,3,4,5,6])
    data = io.re_index_area(data)
    mask = data.index.get_level_values("Area").isin(regiondat.index.get_level_values("Area").to_list())
    data = data[mask]

    io.save(f"data\\{continent}\\{region}", f"Production_Crops_E_{region}", data)

    return
