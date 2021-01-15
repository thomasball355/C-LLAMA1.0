"""
pyFALAFEL-WRAP - Ball, T. 2020
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

import lib.progressbar as progressbar

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

    #regionfinder("Africa", "Eastern Africa", "Western Africa", "Southern Africa", "Northern Africa", "Middle Africa")
    #regionfinder("Americas", "Caribbean", "South America", "Northern America", "Central America")
    #regionfinder("Asia", "Central Asia", "Eastern Asia", "South-Eastern Asia", "Southern Asia", "Western Asia")


    # saves country lists to file to save having to run this script every time (not useful really)
    # for group in group_list:
    #     data = region(FAO_country_metadata, group)
    #     pickle.dump(data, open(f"{wd}\\0area_group_defs\\{group.replace(' ', '').replace('(', '').replace(')', '')}.obj", "wb"))


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

        # pop_dat = data_in.xs("Population", level = "Item")
        # pop_sum = np.sum(pop_dat)

        # pop_mean = pop_dat.mean(axis = 1).mean(level = "Area")
        # pop_mean = pop_mean.sort_values(ascending = False)

        # pop_log = np.log10(pop_mean)

        # pop_perc = (100 * pop_dat.sum(level = "Area") / pop_sum).mean(axis = 1)
        # pop_perc = pop_perc.sort_values(ascending = False)

        # production_dat = data_in.xs("Production", level = "Element").sum(level = "Area")
        # production_sum = np.sum(production_dat)

        # prod_mean = production_dat.iloc[:, -10:-1].mean(axis = 1)
        # prod_mean = prod_mean.sort_values(ascending = False)

        # prod_log = np.log10(prod_mean)
        # prod_log = prod_log.sort_values(ascending = False)

        # prod_perc = (100 * production_dat / production_sum).mean(axis = 1)
        # prod_perc = prod_perc.sort_values(ascending = False)
        # prod_perc_log = np.log10(prod_perc)

        # drop_list = []
        # for item in prod_perc_log.index.to_list():
        #     if prod_perc_log[item] < max(prod_perc_log) - 3:
        #         drop_list.append(item)

        # mask = np.logical_not(data_in.index.get_level_values("Area").isin(drop_list))

        # data_in = data_in[mask]

        # prod_mean = prod_mean[prod_mean > 0]

        # def plot():
        #     cmap = cm.get_cmap("plasma", len(prod_perc_log)+5)
        #     cmap = sns.color_palette(palette = "colorblind")
        #     #plt.style.use("Solarize_Light2")

        #     # plt.scatter(prod_log, pop_log, marker = "x", color = "blue")
        #     # plt.plot(np.unique(prod_log), np.poly1d(np.polyfit(prod_log, pop_log, 1))(np.unique(prod_log)), color = "black")
        #     # plt.xlabel("log10 production (1000 tonnes)")
        #     # plt.ylabel("log10 population (1000 capita)")
        #     # line = stat.linregress(prod_log, pop_log)
        #     # plt.text(min(prod_log)+0.5, max(pop_log)-0.5, f"{round(line[0], 3)}x + {round(line[1], 3)} \nr = {round(line[2], 3)}")
        #     list = ["Venezuela" if x == "Venezuela (Bolivarian Republic of)" else "St Vincent" if x == "Saint Vincent and the Grenadines" else x for x in prod_mean.index.to_list()]
        #     plt.bar(list, prod_mean.values / 1000000, width = 0.9, color = cmap, alpha = 0.8)
        #     plt.grid(alpha = 0.8, axis = "y")
        #     plt.tick_params(axis="x", labelsize=8)
        #     plt.ylabel("Food production (billion tonnes / year)")
        #     plt.xticks(rotation=30, ha = "right")
        #     plt.xlim(-1, len(prod_perc_log))
        #     #plt.plot([-1, len(prod_perc_log) + 1], [max(prod_perc_log) - 3.0, max(prod_perc_log) - 3.0], color = "gray", alpha = 0.9)
        #     plt.show()
        # plot()


        # for item in popdat.index.get_level_values("Area").to_list():
        #     print(item)
        #     #print(100 * popdat.xs(item, level = "Area") / popsum)
        #     #print(100 * production_dat.loc[item] / production_sum)
        #     prod_mean_perc = np.mean(100 * production_dat.loc[item] / production_sum)
        #     prod_dist.append({prod_mean_perc : item})
        # print(prod_dist)

        for group in groups:
            g = group.replace(" ", "").replace("/", "").replace("(", "").replace(")", "").replace("-", "").upper()
            dirs(f"{wd}\\{dataset}", f"{g}")
            country_list = region(FAO_country_metadata, group)["Country"]
            data_out = data_in.iloc[data_in.index.get_level_values("Area").isin(country_list)]

            data_out = io.re_index_area(data_out)
            #data_in = data_in.iloc[data_in.index.get_level_values("Area").isin(country_list)]
            #data_out = data_out.drop(data_out.filter(["Area Code","Item Code","Element Code"]).columns, axis = 1)
            #data_out = data_out.T
            #data_out = data_out.reindex(index)
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
