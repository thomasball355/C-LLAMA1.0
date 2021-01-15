import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.funcs.name_alias
import lib.dat.colours
import lib.dat.food_commodity_seperation as fcs

def main(data, continent, region, area, path):

    def error_rep(comm, type):
        print(f"Warning: KeyError in {__name__} - no {type} data for {comm} in {area}.")
        return


    FAO_comm_groups = pd.read_csv(f"data\\FAOSTAT_data_11-6-2019_commoditygroups.csv")
    # returns the list of items within a commodity group
    def comm_group(metadata, group):
        data = metadata.loc[metadata["Item Group"] == group]
        return data


    # These are taken as individual commodities
    staple_crops = fcs.staple_crops
    # Aggregated groups
    vegetal_prods_grouped_list = fcs.vegetal_prods_grouped_list
    # grouped as luxuries
    luxuries = fcs.luxuries
    # alcohol
    alcohol = fcs.alcohol

    index_list  = staple_crops + vegetal_prods_grouped_list\
                + ["Luxuries (excluding Alcohol)", "Alcohol"]\
                + ["Other"]
    # group commodities
    yield_agg = pd.DataFrame(index = index_list, columns = data.columns.to_list())

    yield_regional_max = pd.DataFrame(index = index_list, columns = ["Value"])

    prod_agg = pd.DataFrame(index = index_list, columns = data.columns.to_list())

    area_agg = pd.DataFrame(index = index_list, columns = data.columns.to_list())


    yield_dat = data.xs("Yield", level = "Element") #hg /ha
    prod_dat = data.xs("Production", level = "Element")
    area_dat = data.xs("Area harvested", level = "Element")

    area_yield_dat = yield_dat.xs(area, level = "Area")
    area_yield_dat = area_yield_dat * 1E-04 # tonnes / ha
    area_prod_dat = prod_dat.xs(area, level = "Area")
    area_area_dat = area_dat.xs(area, level = "Area")


    # Lots of naming conventions changed about here (production dataset doesn't align with FBS).
    for crop in staple_crops:
        if crop == "Rape and Mustardseed":
            div = 0.5
            try:
                yield_agg.loc[crop] = area_yield_dat.xs("Rapeseed", level = "Item").values
                prod_agg.loc[crop] = area_prod_dat.xs("Rapeseed", level = "Item").values
                area_agg.loc[crop] = area_area_dat.xs("Rapeseed", level = "Item").values
            except KeyError:
                div = 1
            try:
                yield_agg.loc[crop] = np.sum([yield_agg.loc[crop],area_yield_dat.xs("Mustard seed", level = "Item").values[0]], axis = 0)
                prod_agg.loc[crop] = np.sum([prod_agg.loc[crop],area_prod_dat.xs("Mustard seed", level = "Item").values[0]], axis = 0)
                area_agg.loc[crop] = np.sum([area_agg.loc[crop],area_area_dat.xs("Mustard seed", level = "Item").values[0]], axis = 0)
            except KeyError:
                div = 1
            yield_agg.loc[crop] = yield_agg.loc[crop] * div
        else:
            try:
                yield_agg.loc[crop] = area_yield_dat.xs(crop, level = "Item").values
                prod_agg.loc[crop] = area_prod_dat.xs(crop, level = "Item").values
                area_agg.loc[crop] = area_area_dat.xs(crop, level = "Item").values
            except KeyError:
                try:
                    yield_agg.loc[crop] = area_yield_dat.xs(lib.funcs.name_alias.conv(crop), level = "Item").values
                    prod_agg.loc[crop] = area_prod_dat.xs(lib.funcs.name_alias.conv(crop), level = "Item").values
                    area_agg.loc[crop] = area_area_dat.xs(lib.funcs.name_alias.conv(crop), level = "Item").values
                except KeyError:
                    error_rep(lib.funcs.name_alias.conv(crop), "production")



    production_groups = pd.read_csv("data\\FAOSTAT_data_1-21-2020_production_dat_groups.csv")

    # This method seems to work for now! Do the same for all grouped commodities

    # Fruit
    fruit_list = comm_group(production_groups, "Fruit Primary")["Item"].to_list()
    fruit = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(fruit_list)]
    yield_agg.loc["Fruits - Excluding Wine"] = fruit.mean(axis = 0).values
    fruit = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(fruit_list)]
    prod_agg.loc["Fruits - Excluding Wine"] = fruit.mean(axis = 0).values
    fruit = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(fruit_list)]
    area_agg.loc["Fruits - Excluding Wine"] = fruit.mean(axis = 0).values


    # Cereal (- wheat, - rice, -maize)
    cereal_list = comm_group(production_groups, "Cereals, Total")["Item"].to_list()
    cereal_list.remove("Wheat")
    cereal_list.remove("Rice, paddy")
    cereal_list.remove("Maize")
    cereal = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(cereal_list)]
    yield_agg.loc["Cereals - Excluding Beer"] = cereal.mean(axis = 0)
    cereal = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(cereal_list)]
    prod_agg.loc["Cereals - Excluding Beer"] = cereal.mean(axis = 0).values
    cereal = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(cereal_list)]
    area_agg.loc["Cereals - Excluding Beer"] = cereal.mean(axis = 0).values


    # Oilcrops (-Soybeans, -Palm oil, -Rapeseed, -Mustard seed, -Sunflower seed)
    oilcrop_list = comm_group(production_groups, "Oilcrops, Oil Equivalent")
    droplist = ["Soybeans", "Oil, palm", "Sunflower seed", "Rapeseed", "Mustard seed"]
    oilcrop_list = oilcrop_list[np.logical_not(oilcrop_list["Item"].isin(droplist))]
    oilcrop = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(oilcrop_list["Item"])]
    yield_agg.loc["Oilcrops"] = oilcrop.mean(axis = 0).values
    oilcrop = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(oilcrop_list["Item"])]
    prod_agg.loc["Oilcrops"] = oilcrop.mean(axis = 0).values
    oilcrop = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(oilcrop_list["Item"])]
    area_agg.loc["Oilcrops"] = oilcrop.mean(axis = 0).values


    # Pulses
    pulses_list = comm_group(production_groups, "Pulses, Total")["Item"].to_list()
    pulses = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(pulses_list)]
    yield_agg.loc["Pulses"] = pulses.mean(axis = 0).values
    pulses = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(pulses_list)]
    prod_agg.loc["Pulses"] = pulses.mean(axis = 0).values
    pulses = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(pulses_list)]
    area_agg.loc["Pulses"] = pulses.mean(axis = 0).values



    # Spices
    spices_list = ["Pepper (piper spp.)", "Cloves", "Spices nes", "Spices, nes", "Anise, badian, fennel, coriander"]
    spices = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(spices_list)]
    yield_agg.loc["Spices"] = spices.mean(axis = 0).values
    spices = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(spices_list)]
    prod_agg.loc["Spices"] = spices.mean(axis = 0).values
    spices = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(spices_list)]
    area_agg.loc["Spices"] = spices.mean(axis = 0).values


    # Starchy roots (- potato, - cassava)
    roots_list = comm_group(production_groups, "Roots and Tubers, Total")["Item"].to_list()
    roots_list.remove("Potatoes")
    roots_list.remove("Cassava")
    roots = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(roots_list)]
    yield_agg.loc["Starchy Roots"] = roots.mean(axis = 0).values
    roots = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(roots_list)]
    prod_agg.loc["Starchy Roots"] = roots.mean(axis = 0).values
    roots = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(roots_list)]
    area_agg.loc["Starchy Roots"] = roots.mean(axis = 0).values


    # Sugar crops
    #sugar_list = ["Honey", "Sugar (Raw Equivalent", "Sugar non-centrifugal", "Sweeteners, Other"]
    sugar_list = ["Sugar cane", "Sugar beet"]
    sugar = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(sugar_list)]
    yield_agg.loc["Sugar & Sweeteners"] = sugar.mean(axis = 0).values
    sugar = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(sugar_list)]
    prod_agg.loc["Sugar & Sweeteners"] = sugar.mean(axis = 0).values
    sugar = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(sugar_list)]
    area_agg.loc["Sugar & Sweeteners"] = sugar.mean(axis = 0).values


    # Vegetable Oils -  an "effective yield"; these crops are the same as oilcrops
    #                   in these cases a factor is applied for oil extraction,
    #                   resulting in a typically lower effective yield.
    oilcrop_list = comm_group(production_groups, "Oilcrops, Oil Equivalent")
    droplist = ["Soybeans", "Oil, palm", "Sunflower seed", "Rapeseed", "Mustard seed"]
    oilcrop_list = oilcrop_list[np.logical_not(oilcrop_list["Item"].isin(droplist))]
    oilcrop = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(oilcrop_list["Item"])]
    prod_agg.loc["Vegetable Oils"] = oilcrop.mean(axis = 0).values
    oilcrop = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(oilcrop_list["Item"])]
    area_agg.loc["Vegetable Oils"] = oilcrop.mean(axis = 0).values
    oilcrop = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(oilcrop_list["Item"])]
    for item in oilcrop.index.get_level_values("Item"):
        factor = oilcrop_list.loc[oilcrop_list['Item'] == item, 'Factor'].iloc[0]
        oilcrop.loc[oilcrop.index.get_level_values("Item") == item] = oilcrop.loc[oilcrop.index.get_level_values("Item") == item] * factor
    yield_agg.loc["Vegetable Oils"] = oilcrop.mean(axis = 0).values


    # Vegetables
    vegetable_list = comm_group(production_groups, "Vegetables Primary")["Item"].to_list()
    vegetables = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(vegetable_list)]
    yield_agg.loc["Vegetables"] = vegetables.mean(axis = 0).values
    vegetables = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(vegetable_list)]
    prod_agg.loc["Vegetables"] = vegetables.mean(axis = 0).values
    vegetables = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(vegetable_list)]
    area_agg.loc["Vegetables"] = vegetables.mean(axis = 0).values


    # luxuries
    luxury_list = ["Cocoa, beans", "Coffee, green", "Tea", "Maté"]
    luxuries_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(luxury_list)]
    prod_agg.loc["Luxuries (excluding Alcohol)"] = luxuries_prod.mean(axis = 0).values
    luxuries_area = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(luxury_list)]
    area_agg.loc["Luxuries (excluding Alcohol)"] = luxuries_area.mean(axis = 0).values
    luxuries_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(luxury_list)]
    yield_agg.loc["Luxuries (excluding Alcohol)"] = luxuries_yield.mean(axis = 0).values


    # Alcohol
    alcohol_list = ["Grapes", "Wheat", "Barley", "Hops"]
    alc_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(alcohol_list)]
    prod_agg.loc["Alcohol"] = alc_prod.mean(axis = 0).values
    alc_area = area_area_dat.iloc[area_area_dat.index.get_level_values("Item").isin(alcohol_list)]
    area_agg.loc["Alcohol"] = alc_area.mean(axis = 0).values
    alc_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(alcohol_list)]
    yield_agg.loc["Alcohol"] = alc_yield.mean(axis = 0).values


    # "Other"
    big_list    = staple_crops + fruit_list + cereal_list + oilcrop_list["Item"].to_list()\
                + sugar_list + pulses_list + spices_list + roots_list\
                + vegetable_list + luxury_list + alcohol_list
    other_list  = ["Flax fibre and tow", "Fibre crops nes", "Tobacco, unmanufactured", "Seed cotton"]
    others_     = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(other_list)]
    yield_agg.loc["Other"] = others_.mean(axis = 0)


    # save
    io.save(f"{path}\\yield_production", f"yield_hist_{area}", yield_agg)

    # add max values to dataframe(for use later)
    maxvals = io.load(f"{path}", "_yield_max_vals_temp")
    maxvals.loc[area] = yield_agg.max(axis = 1)
    io.save(f"{path}", "_yield_max_vals_temp", maxvals)
    minvals = io.load(f"{path}", "_yield_min_vals_temp")
    minvals.loc[area] = yield_agg.min(axis = 1)
    io.save(f"{path}", "_yield_min_vals_temp", minvals)

    ratios = io.load(f"{path}", "_prod_ratios_temp")

    ratios.loc[area] = prod_agg["Y2017"]
    io.save(f"{path}", "_prod_ratios_temp", ratios)
