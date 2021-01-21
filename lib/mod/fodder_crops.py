

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import itertools

import lib.funcs.dat_io as io
import lib.funcs.perc_contributions_WRAP

import lib.dat.colours
import lib.dat.food_commodity_seperation
import lib.dat.livestock_params
import lib.dat.fodder_crops

def main(area_index):

    demand_sum = pd.DataFrame(index = area_index.index, columns = lib.dat.food_commodity_seperation.animal_prods_list + ["Dairy"])

    fodder_list = lib.dat.fodder_crops.fodder_crops

    for continent in area_index.Continent.unique():

        for region in area_index[area_index.Continent == continent].Region.unique():
            path = f"data\\{continent}\\{region}"
            for area in area_index[area_index.Region == region].index.to_list():

                area_feed_demand = io.load(f"{path}\\livestock", f"feed_demand_energy_minus_post_prod_{area}")

                demand_sum.loc[area] = area_feed_demand.iloc[:, :2].mean(axis = 1)

    demand_ratios = demand_sum / np.sum(demand_sum, axis = 0)

    available_residues_sum = pd.DataFrame(index = area_index.index, columns = np.arange(2013, 2051, 1))

    crop_properties = pd.read_excel("lib\\dat\\vegetal_product_properties.xlsx", index_col = 0)

    for continent in area_index.Continent.unique():

        for region in area_index[area_index.Continent == continent].Region.unique():
            path = f"data\\{continent}\\{region}"
            for area in area_index[area_index.Region == region].index.to_list():

                area_residues_harvested = io.load(f"{path}\\harvest_residues", f"harvest_residues_recovered_{area}")

                # convert back to energy
                area_residues_harvested_energy = (area_residues_harvested.T * crop_properties["energy_density"]).T # MJ/year

                available_residues_sum.loc[area] = area_residues_harvested_energy.sum(axis = 0)

    byproduct_feed_potential = lib.dat.livestock_params.byproduct_feed_potential

    agri_feed_potential = pd.DataFrame(data = byproduct_feed_potential).iloc[0]

    fodder_production_ratios = pd.DataFrame(index = area_index.index, columns = fodder_list)

    fodder_demand_projected_sum = pd.DataFrame(index = fodder_list + ["Other feed"], columns = np.arange(2013, 2051, 1), data = 0)

    for continent in area_index.Continent.unique():

        for region in area_index[area_index.Continent == continent].Region.unique():

            path = f"data\\{continent}\\{region}"
            FBS = io.load(f"data\\{continent}\\{region}", f"FoodBalanceSheets_E_{region}")

            for area in area_index[area_index.Region == region].index.to_list():

                area_feed_demand = io.load(f"{path}\\livestock", f"feed_demand_energy_minus_post_prod_{area}")

                FBS_area = FBS.xs(area, level = "Area")

                potential_feed_from_agri_row = (agri_feed_potential * demand_ratios.loc[area]).T#.apply(np.sum(available_residues_sum, axis = 0).values)
                potential_feed_from_agri = pd.DataFrame(1, index = potential_feed_from_agri_row.index, columns = available_residues_sum.columns)
                potential_feed_from_agri = potential_feed_from_agri.multiply(potential_feed_from_agri_row, axis = "index") * np.sum(available_residues_sum, axis = 0)

                ######################
                # multiply by "efficiency": ie, actually used residues based on region
                other_waste_to_feed = io.load(f"{path}\\food_waste", f"waste_ratios_{area}").loc["other_waste_to_feed"]

                for item in area_feed_demand.index.to_list():
                    feed_used = potential_feed_from_agri.loc[item] * other_waste_to_feed.values
                    area_feed_demand.loc[item] = np.where(feed_used > area_feed_demand.loc[item], 0, area_feed_demand.loc[item] - feed_used)

                # Calculate ratios for production and fodder mix (area)
                FBS_area = FBS.xs(area, level = "Area")
                FBS_production = FBS_area.xs("Production", level = "Element")

                FBS_fodder_production = FBS_production[FBS_production.index.isin(fodder_list, level = "Item")]
                FBS_fodder_production_10 = FBS_fodder_production.iloc[:, :-10].mean(axis = 1)

                FBS_fodder_production_10.index = FBS_fodder_production_10.index.get_level_values("Item").to_list()

                for item in fodder_production_ratios.columns.to_list():
                    try:
                        fodder_production_ratios.loc[area].loc[item] = FBS_fodder_production_10.loc[item]
                    except KeyError:
                        fodder_production_ratios.loc[area].loc[item] = 0

                # calculate fodder mix
                FBS_feed = FBS_area.xs("Feed", level = "Element")

                drop_list =     ["Sugar Crops", "Sugar, non-centrifugal", "Sugar (Raw Equivalent)",
                                "Milk - Excluding Butter", "Cereals - Excluding Beer", "Fish, Body Oil",
                                "Fish, Liver Oil", "Demersal Fish", "Pelagic Fish", "Marine Fish, Other",
                                "Oilcrops, Other", "Pulses, Other and products",
                                "Mutton & Goat Meat", "Meat, Other", "Offals, Edible", "Crustaceans",
                                "Cephalopods", "Meat", "Offals", "Animal fats", "Starchy Roots"]

                mask = np.logical_not(FBS_feed.index.get_level_values("Item").isin(drop_list))
                FBS_feed = FBS_feed[mask]
                fodder_mix = FBS_feed[FBS_feed.index.get_level_values("Item").isin(fodder_list + ["Fish, Seafood"])].droplevel(["Unit", "Area Code", "Item Code", "Element Code"])
                mask = np.logical_not(FBS_feed.index.get_level_values("Item").isin(fodder_list + ["Fish, Seafood"]))
                fodder_other = FBS_feed[mask]
                fodder_other = fodder_other.sum(level = "Item").sum(axis = 0)
                fodder_mix.loc["Other feed"] = fodder_other

                for col in fodder_mix:
                    fodder_mix[col] = fodder_mix[col] / np.nansum(fodder_mix[col])

                fodder_mix_projected = lib.funcs.perc_contributions_WRAP.fodder_percentage_contributions(fodder_mix, 2050, 1961, 2013)

                non_crop_2013_factor = 0.08 # calculated using FAO data externally
                fodder_demand_projected = fodder_mix_projected * np.sum(area_feed_demand, axis = 0).values * (1 - non_crop_2013_factor)
                io.save(path, f"livestock\\fodder_demand_projected_{area}", fodder_demand_projected)

                for item in [x for x in fodder_demand_projected.index if x != "Fish, Seafood"]:
                    fodder_demand_projected_sum.loc[item] = np.nansum([fodder_demand_projected_sum.loc[item], fodder_demand_projected.loc[item].values], axis = 0)

    for col in fodder_production_ratios:
        fodder_production_ratios[col] = fodder_production_ratios[col] / np.sum(fodder_production_ratios[col])

    for continent in area_index.Continent.unique():

        for region in area_index[area_index.Continent == continent].Region.unique():

            path = f"data\\{continent}\\{region}"
            FBS = io.load(f"data\\{continent}\\{region}", f"FoodBalanceSheets_E_{region}")

            for area in area_index[area_index.Region == region].index.to_list():

                fodder_production_allocation = (fodder_demand_projected_sum.T * fodder_production_ratios.loc[area]).T

                io.save(path, f"livestock\\fodder_production_quota_{area}", fodder_production_allocation)
