import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os
import scipy.stats as stat

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation
import lib.dat.livestock_params


def main(continent, region, area, path):


    dev_metric = io.load(f"{path}\\dev_metrics", f"dev_metric_{area}")
    food_waste_gen = io.load("lib\\dat\\waste_vars", "food_waste_gen")

    waste_variables         = pd.DataFrame(columns = food_waste_gen.columns, index = ["processing", "distribution", "post_production", "post_production_to_feed", "other_waste_to_feed"])
    waste_variables_diff    = pd.DataFrame(columns = food_waste_gen.columns, index = ["processing", "distribution", "post_production", "post_production_to_feed", "other_waste_to_feed"])

    waste_variables_diff.loc["processing"] = abs(np.subtract(food_waste_gen.loc["processing_high_dev"], food_waste_gen.loc["processing_low_dev"]))
    waste_variables_diff.loc["distribution"] = abs(np.subtract(food_waste_gen.loc["distribution_high_dev"], food_waste_gen.loc["distribution_low_dev"]))
    waste_variables_diff.loc["post_production"] = abs(np.subtract(food_waste_gen.loc["post_prod_high_dev"], food_waste_gen.loc["post_prod_low_dev"]))
    waste_variables_diff.loc["post_production_to_feed"] = abs(np.subtract(food_waste_gen.loc["post_prod_to_feed_high_dev"], food_waste_gen.loc["post_prod_to_feed_low_dev"]))
    waste_variables_diff.loc["other_waste_to_feed"] = abs(np.subtract(food_waste_gen.loc["other_waste_to_feed_high_dev"], food_waste_gen.loc["other_waste_to_feed_low_dev"]))

    waste_variables.loc["processing"]                   = food_waste_gen.loc["processing_low_dev"] - (waste_variables_diff.loc["processing"].values * dev_metric)
    waste_variables.loc["distribution"]                 = food_waste_gen.loc["distribution_low_dev"] - (waste_variables_diff.loc["distribution"].values * dev_metric)
    waste_variables.loc["post_production"]              = (waste_variables_diff.loc["post_production"].values * dev_metric) + food_waste_gen.loc["post_prod_low_dev"]
    waste_variables.loc["post_production_to_feed"]      = - (waste_variables_diff.loc["post_production_to_feed"].values * dev_metric) + food_waste_gen.loc["post_prod_to_feed_low_dev"]
    waste_variables.loc["other_waste_to_feed"]          = (waste_variables_diff.loc["other_waste_to_feed"].values * dev_metric) + food_waste_gen.loc["other_waste_to_feed_low_dev"]

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

    io.save(f"{path}\\food_waste", f"waste_ratios_{area}", waste_variables)

    def fed_without_forage_1():

        fed_without_forage_dev = lib.dat.livestock_params.fed_without_forage_developed
        fed_without_forage_udev = lib.dat.livestock_params.fed_without_forage_developing
        fed_without_forage = pd.DataFrame(index = fed_without_forage_udev, columns = waste_variables.columns)

        for item in fed_without_forage_dev:
            val = lambda x: fed_without_forage_udev[item] + (fed_without_forage_dev[item] - fed_without_forage_udev[item]) * x
            fed_without_forage.loc[item] = [val(x) for x in dev_metric]

        io.save(f"{path}\\livestock", f"fed_without_forage_{area}", fed_without_forage)

    fed_without_forage_1()


    def plot():
        area_list = ["CHINAMAINLAND", "UNITEDSTATESOFAMERICA", "BELIZE", "BRAZIL", "NIGERIA", "CONGO"]

        if area in area_list:
            lw1 = 3
            lw2 = 6
            plt.style.use("Solarize_Light2")

            col1 = "#3B7ACB"
            col2 = "#CB3BC2"
            col3 = "#3BCB44"
            col4 = "#DF8612"

            custom_lines = [Line2D([0], [0], color = col1, lw = "3"), Line2D([0], [0], color = col2, lw = "3"), Line2D([0], [0], color = col3, lw = "3"), Line2D([0], [0], color = col4, lw = "3")]

            # plt.plot(waste_variables.loc["processing"], color = col1, alpha = 1, linewidth = lw1)
            # # plt.plot(food_waste_gen.loc["processing_high_dev"], color = col1, linestyle = "--", alpha = 0.6, linewidth = lw2)
            # # plt.plot(food_waste_gen.loc["processing_low_dev"], color = col1, linestyle = "--", alpha = 0.6, linewidth = lw2)
            # plt.fill_between(np.arange(2013, 2051, 1), food_waste_gen.loc["processing_high_dev"].values.astype("float64"), food_waste_gen.loc["processing_low_dev"].values.astype("float64"), color = col1, alpha = 0.3)

            plt.plot(waste_variables.loc["post_production"], color = col1, alpha = 1, linewidth = lw1)
            #plt.plot(food_waste_gen.loc["post_prod_high_dev"], color = col2, linestyle = "--", alpha = 0.6, linewidth = lw2)
            #plt.plot(food_waste_gen.loc["post_prod_low_dev"], color = col2, linestyle = "--", alpha = 0.6, linewidth = lw2)
            plt.fill_between(np.arange(2013, 2051, 1), food_waste_gen.loc["post_prod_low_dev"].values.astype("float64"), food_waste_gen.loc["post_prod_high_dev"].values.astype("float64"), color = col1, alpha = 0.3)

            # plt.plot(waste_variables.loc["distribution"], color = col3, alpha = 1, linewidth = lw1)
            # # plt.plot(food_waste_gen.loc["distribution_high_dev"], color = col3, linestyle = "--", alpha = 0.6, linewidth = lw2)
            # # plt.plot(food_waste_gen.loc["distribution_low_dev"], color = col3, linestyle = "--", alpha = 0.6, linewidth = lw2)
            # plt.fill_between(np.arange(2013, 2051, 1), food_waste_gen.loc["distribution_high_dev"].values.astype("float64"), food_waste_gen.loc["distribution_low_dev"].values.astype("float64"), color = col1, alpha = 0.3)


            # plt.plot(waste_variables.loc["post_production_to_feed"], color = col2, alpha = 1, linewidth = lw1)
            # # plt.plot(food_waste_gen.loc["post_prod_to_feed_high_dev"], color = col4, linestyle = "--", alpha = 0.6, linewidth = lw2)
            # # plt.plot(food_waste_gen.loc["post_prod_to_feed_low_dev"], color = col4, linestyle = "--", alpha = 0.6, linewidth = lw2)
            # plt.fill_between(np.arange(2013, 2051, 1), food_waste_gen.loc["post_prod_to_feed_high_dev"].values.astype("float64"), food_waste_gen.loc["post_prod_to_feed_low_dev"].values.astype("float64"), color = col2, alpha = 0.3)

            plt.ylabel("Loss ratio")
            plt.xlabel("Year")
            plt.legend(custom_lines, ["Post production"])#, "Post production to feed"])
            plt.ylim(0, 1)
            plt.show()
    #plot()
