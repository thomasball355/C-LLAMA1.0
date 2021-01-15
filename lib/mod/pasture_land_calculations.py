import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.stats as stat

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation
import lib.dat.livestock_params


def main(area_index):

    land_use_dat = pd.read_csv("data\\Inputs_LandUse_E_All_Data_NOFLAG.csv",
                                encoding = "latin-1",
                                index_col = ["Area", 'Item Code',
                                'Item', 'Element Code', 'Element', 'Unit'])
    land_use_dat = io.re_index_area(land_use_dat)

    effective_pasture_yield_hist = pd.DataFrame(columns = np.arange(1961, 2013 + 1, 1), index = area_index.index.to_list())

    grazing_land_cultivated_ratio = pd.DataFrame(columns = np.arange(1961, 2018, 1), index = area_index.index.to_list())

    plot_total_pasture_area = pd.DataFrame(columns = np.arange(2013, 2051, 1), index = area_index.index.to_list())
    plot_total_pasture_area_diff = pd.DataFrame(columns = np.arange(2013, 2051, 1), index = area_index.index.to_list())
    plot_total_pasture_hist = pd.DataFrame(columns = np.arange(1961, 2018, 1), index = area_index.index.to_list())

    conversion_ratios = pd.read_csv("data\\wirsenius_2010_FCR_livestock.csv", index_col=[
                                    "Animal system and parameter", "Scenario"])  # from https://doi.org/10.1016/j.agsy.2010.07.005

    CR_dict = {"Bovine Meat": "Beef cattle meat",
               "Poultry Meat": "Poultry meat",
               "Pigmeat": "Pork (crude carcass)",
               "Mutton & Goat Meat": "Sheep meat"}

    idx = lib.dat.livestock_params.animal_prods_list + ["Dairy"]
    col = conversion_ratios.columns
    arr = []
    for x in idx:
        arr.append(x)
        arr.append(x)
        arr.append(x)

    conversion_ratios_format_1992 = pd.DataFrame(index = idx, columns = col)
    conversion_ratios_format_REF = pd.DataFrame(index = idx, columns = col)
    conversion_ratios_format_ILP = pd.DataFrame(index = idx, columns = col)

    for item in CR_dict:
        conversion_ratios_format_1992.loc[item] = conversion_ratios.xs(
            CR_dict[item], level="Animal system and parameter").loc["1992/1994"].values

    conversion_ratios_format_1992.loc["Eggs"] = conversion_ratios.xs(
        "Egg", level="Animal system and parameter").loc["1992/1994"].values
    conversion_ratios_format_1992.loc["Dairy"] = conversion_ratios.xs(
        "Cattle whole-milk", level="Animal system and parameter").loc["1992/1994"].values
    conversion_ratios_format_1992.loc["Meat, Other"] = np.mean([conversion_ratios.xs("Beef cattle meat", level="Animal system and parameter").loc["1992/1994"].values,
                                                                conversion_ratios.xs(
                                                                    "Poultry meat", level="Animal system and parameter").loc["1992/1994"].values,
                                                                conversion_ratios.xs(
                                                                    "Pork (crude carcass)", level="Animal system and parameter").loc["1992/1994"].values,
                                                                conversion_ratios.xs("Sheep meat", level="Animal system and parameter").loc["1992/1994"].values], axis=0)

    area_dict = {"NORTHERNAMERICA": "North America and Oceania",
                 "SOUTHAMERICA": "Latin America and the Caribbean",
                 "CENTRALAMERICA": "Latin America and the Caribbean",
                 "CARIBBEAN": "Latin America and the Caribbean",
                 "EASTERNAFRICA": "Sub-Saharan Africa",
                 "WESTERNAFRICA": "Sub-Saharan Africa",
                 "NORTHERNAFRICA": "North Africa and West Asia",
                 "SOUTHERNAFRICA": "Sub-Saharan Africa",
                 "MIDDLEAFRICA": "Sub-Saharan Africa",
                 "CENTRALASIA": "South and Central Asia",
                 "EASTERNASIA": "East Asia",
                 "SOUTHEASTERNASIA": "East Asia",
                 "SOUTHERNASIA": "South and Central Asia",
                 "WESTERNASIA": "North Africa and West Asia",
                 "EASTERNEUROPE": "East Europe",
                 "WESTERNEUROPE": "West Europe",
                 "NORTHERNEUROPE": "West Europe",
                 "SOUTHERNEUROPE": "World average",
                 "AUSTRALIAANDNEWZEALAND": "North America and Oceania",
                 "MICRONESIA": "World average",
                 "POLYNESIA": "World average",
                 "MELANESIA": "World average"
                 }

    pd.set_option("display.max_rows", None)

    for continent in area_index.Continent.unique():

        for region in area_index[area_index.Continent == continent].Region.unique():

            path = f"data\\{continent}\\{region}"
            FBS_dat = io.load(f"data\\{continent}\\{region}", f"FoodBalanceSheets_E_{region}")

            for area in area_index[area_index.Region == region].index.to_list():

                land_use_dat_area = land_use_dat.xs(area, level = "Area").xs("Area", level = "Element")
                land_use_dat_area = land_use_dat_area.iloc[:, 1:]
                FBS_area = FBS_dat.xs(area, level = "Area")

                # calculate proportion of livestock fed without forage
                forage_fed = pd.DataFrame(index = lib.dat.livestock_params.animal_prods_list + lib.dat.livestock_params.dairy,
                                                    columns = np.arange(2013, 2051, 1))
                feed_dat = FBS_area.xs("Feed", level = "Element")                                                                                   # 1000 tonnes / year
                production_dat = FBS_area.xs("Production", level = "Element")                                                                       # 1000 tonnes / year

                anim_non_dairy = production_dat[production_dat.index.get_level_values("Item").isin(lib.dat.livestock_params.animal_prods_list)]

                anim_dairy = production_dat[production_dat.index.get_level_values("Item").isin(lib.dat.livestock_params.dairy)]

                production_mass_demand_hist = pd.DataFrame(index = lib.dat.livestock_params.animal_prods_list +\
                                                    ["Dairy"],
                                                    columns = anim_non_dairy.columns.to_list())
                production_mass_demand_hist_non_pasture = pd.DataFrame(index = lib.dat.livestock_params.animal_prods_list +\
                                                    ["Dairy"],
                                                    columns = anim_non_dairy.columns.to_list())
                # production_energy_hist = pd.DataFrame(index = lib.dat.livestock_params.animal_prods_list +\
                #                                     ["Dairy"],
                #                                     columns = anim_non_dairy.columns.to_list())

                pasture_factor = lib.dat.livestock_params.pasture_factor


                for item in lib.dat.livestock_params.animal_prods_list:

                    ratio = conversion_ratios_format_1992.loc[item].loc[area_dict[region]]

                    try:
                        anim_non_dairy_item = anim_non_dairy.xs(item, level = "Item") # 1000 tonnes / year
                        vals = (anim_non_dairy_item * ratio).mean(axis = 0) # gets rid of duplicate values (ie, eggs are counted twice for some reason)
                        production_mass_demand_hist.loc[item] = vals.values * pasture_factor[item]          # 1000 tonnes / year **
                        production_mass_demand_hist_non_pasture.loc[item]   = vals.values \
                                                                            * (1 - pasture_factor[item])    # 1000 tonnes / year **
                    except KeyError:
                        production_mass_demand_hist.loc[item] = 0
                        production_mass_demand_hist_non_pasture.loc[item] = 0

                production_mass_demand_hist.loc["Dairy"]    = anim_dairy.sum(axis = 0) \
                                                            * conversion_ratios_format_1992.loc["Dairy"][area_dict[region]]
                production_mass_demand_hist_sum = production_mass_demand_hist.sum(axis = 0) # 1000 tonnes / year **

                ##### REMOVE CHICKENS AND PIGS FROM FEED DAT #####
                anim_dairy = anim_dairy.iloc[:3, :]
                anim_non_dairy = anim_non_dairy.iloc[:-1, :]
                prod_ratio = pd.concat([anim_non_dairy, anim_dairy])
                for col in prod_ratio:
                    prod_ratio[col] = prod_ratio[col] / np.sum(prod_ratio[col])

                pasture_animal_ratio = prod_ratio[prod_ratio.index.get_level_values("Item").isin(["Bovine Meat", "Meat, Other", "Mutton & Goat Meat", "Milk - Excluding Butter", "Cream", "Butter, Ghee"])]

                pasture_fed_hist_mass = production_mass_demand_hist_sum - (feed_dat.sum(axis = 0) * (pasture_animal_ratio.sum(axis = 0))) # 1000 tonnes / year **

                def line(dat, dat_start, dat_end):
                    years = np.arange(dat_start, dat_end + 1, 1)
                    line_params = stat.linregress(years, dat)
                    return line_params

                # line_params = line(forage_fed_hist_mass[-40:], 2013 - 39, 2013)
                # slope = line_params[0]
                # inter = line_params[1]
                # r = line_params[2]
                # p = line_params[3]
                #
                # if r**2 > 0.2:
                #     val = lambda x: (x * slope) + inter
                #     forage_fed_projected = [0 if val(x) <= 0 else val(x) if val(x) <= 1.0 else 1.0 for x in np.arange(2013, 2051, 1)]
                # else:
                #     forage_fed_projected = [np.mean(forage_fed_hist_mass[-10:]) for x in np.arange(2013, 2051, 1)]
                #
                # def plot():
                #     area_list = ["CHINAMAINLAND", "UNITEDSTATESOFAMERICA", "BELIZE", "BRAZIL", "NIGERIA", "CONGO"]
                #     if area in area_list:
                #         plt.scatter(np.arange(1961, 2014, 1), forage_fed_hist_mass)
                #         plt.plot(np.arange(2013, 2051, 1), forage_fed_projected)
                #         plt.ylim(0, 1)
                #         plt.show()
                # #plot()

                try:
                    perm_pasture = land_use_dat_area.xs("Land under perm. meadows and pastures", level = "Item").fillna(0)
                except KeyError:
                    perm_pasture = (land_use_dat_area.xs("Agriculture", level = "Item") * 0).fillna(0)
                    print(f"No data for \"Land under perm. meadows and pastures\" in {area}")
                try:
                    temp_pasture = land_use_dat_area.xs("Land under temp. meadows and pastures", level = "Item").fillna(0)
                except KeyError:
                    temp_pasture = (land_use_dat_area.xs("Agriculture", level = "Item") * 0).fillna(0)
                    print(f"No data for \"Land under temp. meadows and pastures\" in {area}")

                total_pasture = perm_pasture + temp_pasture.values # 1000 Ha

                # total_pasture.T.plot()
                # plt.show()
                # plt.plot(pasture_fed_hist_mass)
                # plt.show()

                effective_pasture_yield_hist.loc[area] = pasture_fed_hist_mass.values / total_pasture.iloc[:, :-4].values # tonnes per hectare, 1000s cancel

                dat_2 = effective_pasture_yield_hist.loc[area].values.astype("float32")

                years = 30
                line_params = line(dat_2[-years:], 2013 - (years-1), 2013)
                slope = line_params[0]
                inter = line_params[1]
                r = line_params[2]
                p = line_params[3]

                val = lambda x: ((x * slope) + inter)

                val_2013 = val(2013)
                val_2050 = val(2050)

                if r**2 > 0.3 and p < 0.05 and 0.66 < (val_2050/val_2013) < 1.5:
                    min = np.min(dat_2)
                    max = np.max(dat_2)
                    effective_pasture_mass_yield_projected = [min if val(x) <= min else val(x) for x in np.arange(2013, 2051, 1)] # if val(x) <= max else max
                else:
                    effective_pasture_mass_yield_projected = [np.mean(effective_pasture_yield_hist.loc[area].values[-years:]) for x in np.arange(2013, 2051, 1)]

                def plot():
                    plt.plot(np.arange(2013, 2051, 1), effective_pasture_mass_yield_projected)
                    plt.scatter(np.arange(1961, 2014, 1), effective_pasture_yield_hist.loc[area])
                    plt.show()
                #plot()

                energy_density = lib.dat.livestock_params.energy_density # MJ/kg

                pasture_energy_demand_projection = io.load(path, f"livestock\\forage_feed_energy_{area}") # MJ/year

                pasture_mass_demand_projection = pd.DataFrame(columns = pasture_energy_demand_projection.columns,
                                                                index = pasture_energy_demand_projection.index)

                for item in pasture_energy_demand_projection.index.to_list():

                    pasture_mass_demand_projection.loc[item] = (pasture_energy_demand_projection.loc[item] * pasture_factor[item]) / (energy_density[item] * 1000) #tonnes/year

                def method_2():

                    grazing_intensity_rosegrant_2009 = lib.dat.livestock_params.grazing_intensity_rosegrant_2009
                    area_dict = {"NORTHERNAMERICA": "NAE",
                                 "SOUTHAMERICA": "LAC",
                                 "CENTRALAMERICA": "LAC",
                                 "CARIBBEAN": "LAC",
                                 "EASTERNAFRICA": "SSA",
                                 "WESTERNAFRICA": "SSA",
                                 "NORTHERNAFRICA": "CWANA",
                                 "SOUTHERNAFRICA": "SSA",
                                 "MIDDLEAFRICA": "SSA",
                                 "CENTRALASIA": "CWANA",
                                 "EASTERNASIA": "ESAP",
                                 "SOUTHEASTERNASIA": "ESAP",
                                 "SOUTHERNASIA": "ESAP",
                                 "WESTERNASIA": "CWANA",
                                 "EASTERNEUROPE": "NAE",
                                 "WESTERNEUROPE": "NAE",
                                 "NORTHERNEUROPE": "NAE",
                                 "SOUTHERNEUROPE": "NAE",
                                 "AUSTRALIAANDNEWZEALAND": "ESAP",
                                 "MICRONESIA": "ESAP",
                                 "POLYNESIA": "ESAP",
                                 "MELANESIA": "ESAP"
                                 }
                    values = [x * 250 for x in grazing_intensity_rosegrant_2009[area_dict[region]]] # kg / ha == tonne / 1000 Ha
                    y2000, y2030, y2050 = values[0], values[1], values[2]
                    inc_30 = (y2030 - y2000) / 30
                    inc_20 = (y2050 - y2030) / 20
                    line = [y2000 + (inc_30 * x) if x < 31 else y2030 + (inc_20 * (x-30)) for x in range(0, 51)]

                    return line

                effective_pasture_mass_yield_projected_2 = method_2()

                total_pasture_area = (np.sum(pasture_mass_demand_projection, axis = 0) / 1) / effective_pasture_mass_yield_projected # hectares

                # total_pasture_area = (np.sum(pasture_mass_demand_projection, axis = 0)) / effective_pasture_mass_yield_projected_2[13:]

                plot_total_pasture_area.loc[area] = total_pasture_area

                delta_area = total_pasture_area - total_pasture_area.values[0]

                val = lambda x: x + total_pasture.values[0][-4]
                plot_total_pasture_area_diff.loc[area] = [0 if val(x) < 0 else val(x) for x in delta_area]

                plot_total_pasture_hist.loc[area] = total_pasture.values[0]

                def plot():
                    plt.plot(np.arange(1961, 2018, 1), total_pasture.values[0])
                    plt.plot(plot_total_pasture_area_diff.loc[area])
                    plt.show()
                    # plt.plot(np.arange(1961, 2014, 1), total_pasture.iloc[:, :-4].values[0])
                    # plt.plot(np.arange(2013, 2051, 1), total_pasture_area)
                    # plt.show()
                #plot()

                io.save(f"{path}\\land_use", f"pasture_area_{area}", total_pasture_area)

    # plot_total_pasture_area[plot_total_pasture_area.mean(axis = 1) > 0.0E+07].T.plot()
    # plt.show()

    # plot_total_pasture_area_diff[plot_total_pasture_area_diff.mean(axis = 1) > 0.0E+07].T.plot()
    # plt.show()
    #
    # plt.plot(np.arange(2013, 2051, 1), np.sum(plot_total_pasture_area, axis = 0))
    # #plt.plot(np.arange(2013, 2051, 1), np.sum(plot_total_pasture_area_diff, axis = 0))
    # plt.plot(np.arange(1961, 2018, 1), np.sum(plot_total_pasture_hist, axis = 0))
    # plt.show()
