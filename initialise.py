"""
Functions for initialisation of the model.
"""
import sys
import subprocess
import pkg_resources


while True:
    try:
        import sys
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import os
        import pickle
        import math
        import scipy
        break
    except ModuleNotFoundError:
        print("Checking dependencies...")
        required = {'pandas', 'xlrd', 'pickle-mixin', 'scipy', 'seaborn', 'matplotlib'}
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = required - installed
        if missing:
            try:
                print("Attempting to fetch missing...")
                python = sys.executable
                pip_upgrade = [python, "-m", "pip", "install", "--upgrade", "pip"]
                subprocess.check_call(pip_upgrade)
                package_install = [python, '-m', 'pip', 'install', *missing]
                subprocess.check_call(package_install)
                print("Requirements met, proceeding...")
            except subprocess.CalledProcessError:
                print(f"Installation of missing packages: {missing} failed. This is likely because you are running this without admin rights. Manual installation of packages should solve this problem.")
                quit()
import data_sort
import lib.funcs.dat_io as io
import lib.dat.continents
import lib.dat.food_commodity_seperation as fcs

# sort the population data from the IIASA data into a more usable format for
# the model

def population_sort():

    dat = pd.read_excel("data\\iamc_db_SSP2.xlsx", index_col = [0, 1, 2, 3, 4, 24])
    dat = dat.dropna()
    area_index_prelim = generate_area_index()
    pop_dat_out = pd.DataFrame(columns = dat.columns.to_list(), index = area_index_prelim.index.to_list())

    area_code_index = pd.read_excel("data\\ISO3166-1_codes_and_country_names.xlsx", index_col = 1)
    area_code_index_new = pd.DataFrame(index = io.format_upper(area_code_index.index.to_list()), columns = area_code_index.columns.to_list())


    for i in range(0, len(area_code_index_new)):
        area_code_index_new.iloc[i] = area_code_index.iloc[i]

    for item in area_index_prelim.index.to_list():
        if item in area_code_index_new.index.to_list():
            key = area_code_index_new.loc[item].values[0]
            try:
                for col in pop_dat_out:
                    pop_dat_out[col].loc[item] = dat.xs(key, level = "Region")[col].values[0]
            except KeyError:
                pass
        else:
            pass


    # lots of annoying differences in naming. eg-UK is UK + NI in the naming from IIASA
    for col in pop_dat_out:

        pop_dat_out[col].loc["UNITEDKINGDOM"]                       = dat.xs("GBR", level = "Region")[col].values[0]
        # Former YGSLV is aggregated into this group
        pop_dat_out[col].loc["YUGOSLAVSFR"]                         = dat.xs("MKD", level = "Region")[col].values[0]
        # Micronesian islands
        pop_dat_out[col].loc["KIRIBATI"]                            = dat.xs("FSM", level = "Region")[col].values[0]
        # Taiwan
        #pop_dat_out[col].loc["CHINA,TAIWANPROVINCEOF"]  = dat.xs("TWN", level = "Region")[col].values[0]
        # China
        pop_dat_out[col].loc["CHINA,MAINLAND"]                      = dat.xs("CHN", level = "Region")[col].values[0]
        # Czech Republic
        pop_dat_out[col].loc["CZECHIA"]                             = dat.xs("CZE", level = "Region")[col].values[0]
        # Not sure why this didn't scan
        pop_dat_out[col].loc["DEMOCRATICPEOPLESREPUBLICOFKOREA"]    = dat.xs("PRK", level = "Region")[col].values[0]
        # Cape Verde
        pop_dat_out[col].loc["CABOVERDE"]                           = dat.xs("CPV", level = "Region")[col].values[0]
        # Ivory Coast
        pop_dat_out[col].loc["CÔTEDIVOIRE"]                         = dat.xs("CIV", level = "Region")[col].values[0]
        # Laos
        pop_dat_out[col].loc["LAOPEOPLESDEMOCRATICREPUBLIC"]        = dat.xs("LAO", level = "Region")[col].values[0]

    # drop these because they no longer exist (ie, don't need to be projected)
    drop_list = ["ETHIOPIAPDR", "SERBIAANDMONTENEGRO", "BELIGIUMLUXEMBOURG", "USSR", "SUDANFORMER"]
    mask = np.logical_not(pop_dat_out.index.isin(drop_list))
    pop_dat_out = pop_dat_out[mask]

    io.save("lib\\dat\\population", "SSP2_population_trajectory_raw", pop_dat_out)

    def pop_interpolate(data):

        dat_interpolate = pd.DataFrame(columns = np.arange(2010, 2100, 1), index = data.index.to_list())

        for col in dat_interpolate:
            drange = 5 * math.ceil((col+1)/5)
            dy = data[drange] - data[drange - 5]
            dx = 5
            if col not in data:
                dat_interpolate[col] = data[drange - 5] + ((dy / dx) * (col - drange + 5))
            else:
                dat_interpolate[col] = data[col]

        return dat_interpolate

    io.save("lib\\dat\\population", "SSP2_population_trajectory_interpolated", pop_interpolate(pop_dat_out))


def generate_area_index():

    continents = lib.dat.continents.continents

    country_index       = []
    region_index        = []
    continent_index     = []
    path_index          = []

    waste_energy_frame  = pd.DataFrame(0,   index = ["post_production", "processing", "distribution", "post_production_to_feed"],
                                            columns = np.arange(2013, 2050 + 1, 1))
    max_vals_frame = pd.DataFrame(columns   = fcs.big_list)


    for continent in continents:

        for region in continents[continent]:

            # format
            region = io.format_upper(region)
            string1 = f"data\\{continent}\\{region}\\FoodBalanceSheets_E_{region}.obj"
            string2 = f"data\\{continent}\\{region}\\Production_Crops_E_{region}.obj"

            if os.path.isfile(string1) == False:
                data_sort.data_produce(continent, continents[continent])
            if os.path.isfile(string2) == False:
                data_sort.crop_production_data(continent, region)

            data = io.load(f"data\\{continent}\\{region}", f"FoodBalanceSheets_E_{region}")

            for area in data.xs("Population", level = "Item").index.get_level_values("Area").to_list():
                area = io.format_upper(area)
                country_index.append(area)
                region_index.append(region)
                continent_index.append(continent)
                path_index.append(f"data\\{continent}\\{region}")

            # Used to store max values for vars (eg - yield)
            io.save(f"data\\{continent}\\{region}", f"_yield_max_vals_temp", max_vals_frame)
            io.save(f"data\\{continent}\\{region}", f"_yield_min_vals_temp", max_vals_frame)
            io.save(f"data\\{continent}\\{region}", f"_prod_ratios_temp", max_vals_frame)
            # Used for sums of food_waste_energy
    #         io.save(f"data\\{continent}\\{region}", f"_waste_energy_sums_regional_temp", waste_energy_frame)
    #     io.save(f"data\\{continent}", f"_waste_energy_sums_continent_temp", waste_energy_frame)
    # io.save(f"data", f"_waste_energy_sums_global_temp", waste_energy_frame)

    area_index_prelim = pd.DataFrame(index = country_index, columns = ["Region", "Continent", "Path"])
    area_index_prelim["Region"]    = region_index
    area_index_prelim["Continent"] = continent_index
    area_index_prelim["Path"]      = path_index

    null_list = ["ETHIOPIAPDR", "SUDANFORMER", "USSR", "SERBIAANDMONTENEGRO"]
    area_index_prelim = area_index_prelim[np.logical_not(area_index_prelim.index.isin(null_list))]

    # drop based on land area
    def land_drop():
        land_use_dat = pd.read_csv("data\\Inputs_LandUse_E_All_Data_NOFLAG.csv",
        encoding = "latin-1",
        index_col = ["Area", 'Item Code',
        'Item', 'Element Code', 'Element', 'Unit'])
        land_use_dat = io.re_index_area(land_use_dat)
    
        land_area = land_use_dat.xs("Land area", level = "Item")
    
        cutoff_VANUATU = 1219
    
        land_area_keep = land_area[land_area.mean(axis = 1) > cutoff_VANUATU]
    
        return land_area_keep.index.get_level_values("Area").to_list()    
    
    # keep_list = land_drop()
    
    def prod_drop():
        prod_africa = pd.read_csv("C-LLAMA\\data\\Production_Crops_E_Africa_NOFLAG.csv",
                          encoding = "latin-1",
                          index_col=[0,1,2,3,4,5,6])
        prod_americas = pd.read_csv("C-LLAMA\\data\\Production_Crops_E_Americas_NOFLAG.csv",
                                  encoding = "latin-1",
                                  index_col=[0,1,2,3,4,5,6])
        prod_europe = pd.read_csv("C-LLAMA\\data\\Production_Crops_E_Europe_NOFLAG.csv",
                                  encoding = "latin-1",
                                  index_col=[0,1,2,3,4,5,6])
        prod_asia = pd.read_csv("C-LLAMA\\data\\Production_Crops_E_Asia_NOFLAG.csv",
                                  encoding = "latin-1",
                                  index_col=[0,1,2,3,4,5,6])
        prod_oceania = pd.read_csv("C-LLAMA\\data\\Production_Crops_E_Oceania_NOFLAG.csv",
                                  encoding = "latin-1",
                                  index_col=[0,1,2,3,4,5,6])       
        production = pd.concat([prod_africa, 
                               prod_americas, 
                               prod_americas, 
                               prod_europe, 
                               prod_oceania])       
        production = production.xs("Production", level = "Element")        
        mask = production.index.get_level_values("Item Code").isin(np.arange(0,1000,1))
        production = production[mask]
        production_sum = production.sum(level = "Area")
        p2017 = production_sum["Y2017"].sort_values(ascending = False)
        p2017 = p2017[p2017 > 0]
        perc, k = 0, 0
        while perc < 99.7:
            perc = np.sum(p2017[:k]) / np.sum(p2017[:]) * 100
            k += 1
            
        return p2017[:k].to_list()
    
    keep_list = prod_drop()
    
    area_index_prelim = area_index_prelim[area_index_prelim.index.isin(keep_list)]

    dev_met_temp = pd.DataFrame(index = area_index_prelim.index.to_list(), columns = np.arange(1961, 2014, 1))

    io.save("lib\\dat", f"dev_met_hist", dev_met_temp)

    return area_index_prelim
