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

    # Fruit
    fruit_list = comm_group(production_groups, "Fruit Primary")["Item"].to_list()
    fruit_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(fruit_list)]
    idx = fruit_yield.index.get_level_values("Item").to_list()
    fruit_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    fruit_weighted = (fruit_yield * fruit_prod.values) / fruit_prod.sum(axis = 0).values
    yield_agg.loc["Fruits - Excluding Wine"] = fruit_weighted.sum(axis = 0)

    # Cereal (- wheat, - rice, -maize)
    cereal_list = comm_group(production_groups, "Cereals, Total")["Item"].to_list()
    cereal_list.remove("Wheat")
    cereal_list.remove("Rice, paddy")
    cereal_list.remove("Maize")
    cereal_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(cereal_list)]
    idx = cereal_yield.index.get_level_values("Item").to_list()
    cereal_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    cereal_weighted = (cereal_yield * cereal_prod.values) / cereal_prod.sum(axis = 0).values
    yield_agg.loc["Cereals - Excluding Beer"] = cereal_weighted.sum(axis = 0)

    # Pulses
    pulses_list = comm_group(production_groups, "Pulses, Total")["Item"].to_list()
    pulses_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(pulses_list)]
    idx = pulses_yield.index.get_level_values("Item").to_list()
    pulses_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    pulses_weighted = (pulses_yield * pulses_prod.values) / pulses_prod.sum(axis = 0).values
    yield_agg.loc["Pulses"] = pulses_weighted.sum(axis = 0)

    # Spices
    spices_list = ["Pepper (piper spp.)", "Cloves", "Spices nes", "Spices, nes", "Anise, badian, fennel, coriander"]
    spices_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(spices_list)]
    idx = spices_yield.index.get_level_values("Item").to_list()
    spices_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    spices_weighted = (spices_yield * spices_prod.values) / spices_prod.sum(axis = 0).values
    yield_agg.loc["Spices"] = spices_weighted.sum(axis = 0)

    # Starchy roots (- potato, - cassava)
    roots_list = comm_group(production_groups, "Roots and Tubers, Total")["Item"].to_list()
    roots_list.remove("Potatoes")
    roots_list.remove("Cassava")
    roots_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(roots_list)]
    idx = roots_yield.index.get_level_values("Item").to_list()
    roots_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    roots_weighted = (roots_yield * roots_prod.values) / roots_prod.sum(axis = 0).values
    yield_agg.loc["Starchy Roots"] = roots_weighted.sum(axis = 0)

    # Sugar crops
    sugar_list = ["Sugar cane", "Sugar beet"]
    sugar_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(sugar_list)]
    idx = sugar_yield.index.get_level_values("Item").to_list()
    sugar_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    sugar_weighted = (sugar_yield * sugar_prod.values) / sugar_prod.sum(axis = 0).values
    yield_agg.loc["Sugar & Sweeteners"] = sugar_weighted.sum(axis = 0)

    # Vegetable Oils -  an "effective yield"; these crops are the same as oilcrops
    #                   in these cases a factor is applied for oil extraction,
    #                   resulting in a typically lower effective yield.
    oilcrop_list = comm_group(production_groups, "Oilcrops, Oil Equivalent")
    droplist = ["Soyabeans", "Oil, Palm", "Sunflower seed", "Rapeseed", "Mustard seed"]
    oilcrop_list = oilcrop_list[np.logical_not(oilcrop_list["Item"].isin(droplist))]
    oilcrop_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(oilcrop_list["Item"].to_list())]
    idx = oilcrop_yield.index.get_level_values("Item").to_list()
    oilcrop_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    oilcrop_weighted = (oilcrop_yield * oilcrop_prod.values) / oilcrop_prod.sum(axis = 0).values
    for item in oilcrop_weighted.index.get_level_values("Item"):
        factor = oilcrop_list.loc[oilcrop_list['Item'] == item, 'Factor'].iloc[0]
        oilcrop_weighted.loc[oilcrop_weighted.index.get_level_values("Item") == item] = \
        oilcrop_weighted.loc[oilcrop_weighted.index.get_level_values("Item") == item] * factor
    yield_agg.loc["Oilcrops"] = oilcrop_weighted.sum(axis = 0)

    # Vegetables
    vegetable_list = comm_group(production_groups, "Vegetables Primary")["Item"].to_list()
    vegetable_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(vegetable_list)]
    idx = vegetable_yield.index.get_level_values("Item").to_list()
    vegetable_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    vegetable_weighted = (vegetable_yield * vegetable_prod.values) / vegetable_prod.sum(axis = 0).values
    yield_agg.loc["Vegetables"] = vegetable_weighted.sum(axis = 0)

    # luxuries
    luxury_list = ["Cocoa, beans", "Coffee, green", "Tea", "Maté"]
    luxury_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(luxury_list)]
    idx = luxury_yield.index.get_level_values("Item").to_list()
    luxury_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    luxury_weighted = (luxury_yield * luxury_prod.values) / luxury_prod.sum(axis = 0).values
    yield_agg.loc["Luxuries (excluding Alcohol)"] = luxury_weighted.sum(axis = 0)

    # Alcohol
    alcohol_list = ["Grapes", "Wheat", "Barley", "Hops"]
    alcohol_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(alcohol_list)]
    idx = alcohol_yield.index.get_level_values("Item").to_list()
    alcohol_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    alcohol_weighted = (alcohol_yield * alcohol_prod.values) / alcohol_prod.sum(axis = 0).values
    yield_agg.loc["Alcohol"] = alcohol_weighted.sum(axis = 0)

    # "Other"
    big_list    = staple_crops + fruit_list + cereal_list + oilcrop_list["Item"].to_list()\
                + sugar_list + pulses_list + spices_list + roots_list\
                + vegetable_list + luxury_list + alcohol_list

    others_list  = ["Flax fibre and tow", "Fibre crops nes", "Tobacco, unmanufactured", "Seed cotton"]
    others_yield = area_yield_dat.iloc[area_yield_dat.index.get_level_values("Item").isin(others_list)]
    idx = others_yield.index.get_level_values("Item").to_list()
    others_prod = area_prod_dat.iloc[area_prod_dat.index.get_level_values("Item").isin(idx)]
    others_weighted = (others_yield * others_prod.values) / others_prod.sum(axis = 0).values
    yield_agg.loc["Other"] = others_weighted.sum(axis = 0)

    # save
    io.save(f"{path}\\yield_production", f"yield_hist_{area}", yield_agg)

    # add max values to dataframe(for use later)
    maxvals = io.load(f"{path}", "_yield_max_vals_temp")
    maxvals.loc[area] = yield_agg.max(axis = 1)
    io.save(f"{path}", "_yield_max_vals_temp", maxvals)
    minvals = io.load(f"{path}", "_yield_min_vals_temp")
    minvals.loc[area] = yield_agg.min(axis = 1)
    io.save(f"{path}", "_yield_min_vals_temp", minvals)
