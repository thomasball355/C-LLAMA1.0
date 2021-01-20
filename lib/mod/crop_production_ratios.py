import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys


import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation



def main(area_index):

    # Butchered from the "diet_makeup" module
    def dirs(directory, *args):
        string = f"{directory}\\"
        for arg in args:
            string += f"\\{arg}"
        if os.path.isdir(string) == False:
            os.makedirs(string)
            print(f"Made dir \"{string}\"")

    def error_rep(comm):
        print(f"Warning: KeyError in {__name__} - no data for {comm} in {area}.")
        return

    # returns the list of items within a commodity group
    def comm_group(metadata, group):
        data = metadata.loc[metadata["Item Group"] == group]
        return data

    FAO_comm_groups = pd.read_csv(f"data\\FAOSTAT_data_11-6-2019_commoditygroups.csv")
    # These are taken as individual commodities
    staple_crops = lib.dat.food_commodity_seperation.staple_crops
    # Aggregated groups
    vegetal_prods_grouped_list = lib.dat.food_commodity_seperation.vegetal_prods_grouped_list
    # grouped as luxuries
    luxuries = lib.dat.food_commodity_seperation.luxuries
    alcohol = lib.dat.food_commodity_seperation.alcohol
    # animal products taken as individual commodities
    animal_prods_list = lib.dat.food_commodity_seperation.animal_prods_list
    # grouped as dairy
    dairy = lib.dat.food_commodity_seperation.dairy


    def veggies(data, continent, region, area):

        data = data.xs("Production", level = "Element")
        data = data.iloc[data.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Vegetal Products")["Item"])]

        # create dataframes for output
        vegetal = pd.DataFrame(index = staple_crops + vegetal_prods_grouped_list + ["Luxuries (excluding Alcohol)", "Alcohol"] + ["Other"], columns = data.columns.to_list())

        # key crops have their own trajectory
        for crop in staple_crops:

            if area == "UNITEDSTATESOFAMERICA" and crop == "Maize and products":
                modifier = 0.75
            else:
                modifier = 1.0

            try:
                crop_supp = data.xs(crop, level = "Item").values * modifier
            except KeyError:
                crop_supp = 0
                error_rep(crop)
            vegetal.loc[crop] = np.nansum(crop_supp, axis = 0)

        # remove key crop groups so they don't get included in the aggregated groups
        mask = np.logical_not(data.index.get_level_values("Item").isin(staple_crops + ["Sugar (Raw Equivalent)"]))
        data = data[mask]

        # aggregated crop groups
        for group in vegetal_prods_grouped_list:
            if area == "BRAZIL" and crop == "Sugar ":
                modifier = 0.359
            else:
                modifier = 1.0

            item_list = [x for x in comm_group(FAO_comm_groups, group)["Item"] if x not in staple_crops]
            group_dat = data.iloc[data.index.get_level_values("Item").isin(item_list)]
            vegetal.loc[group] = np.sum(group_dat, axis = 0) * modifier
            # remove grouped items
            mask = np.logical_not(data.index.get_level_values("Item").isin(item_list))
            data = data[mask]
        # remove aggregated groups to leave the "stragglers" (luxuries and misc)
        mask = np.logical_not(data.index.get_level_values("Item").isin(vegetal_prods_grouped_list))
        data = data[mask]


        # Aggregate Luxuries
        luxuries_sum = pd.DataFrame(index = luxuries, columns = data.columns.to_list())
        for food in luxuries:
            try:
                luxuries_sum.loc[food] = data.xs(food, level = "Item").values
            except KeyError:
                error_rep(food)
                luxuries_sum.loc[food] = 0
        vegetal.loc["Luxuries (excluding Alcohol)"] = np.sum(luxuries_sum, axis = 0)
        mask = np.logical_not(data.index.get_level_values("Item").isin(luxuries))
        data = data[mask]

        # Alcohol separate to luxuries
        alcohol_sum = pd.DataFrame(index = alcohol, columns = data.columns.to_list())
        for drink in alcohol:
            try:
                supp = data.xs(drink, level = "Item")
            except KeyError:
                supp = 0
                error_rep(drink)
            alcohol_sum.loc[drink] = np.sum(supp, axis = 0)
        vegetal.loc["Alcohol"] = np.sum(alcohol_sum, axis = 0)
        mask = np.logical_not(data.index.get_level_values("Item").isin(alcohol))
        data = data[mask]


        # Remaining food in vegetal is "Other"
        misc_running_sum = pd.DataFrame(index = data.index.get_level_values("Item"), columns = data.columns.to_list())
        remaining = []
        for item in data.index.get_level_values("Item").to_list():
            if item not in remaining:
                remaining.append(item)
        for item in remaining:
            try:
                food_supp = data.xs(item, level = "Item").values
            except KeyError:
                food_supp = 0
            misc_running_sum.loc[item] = food_supp
        vegetal.loc["Other"] = np.sum(misc_running_sum, axis = 0)


        return vegetal



    def animals(data, continent, region, area):

        data = data.xs("Production", level = "Element")
        data = data.iloc[data.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Animal Products")["Item"])]

        animal = pd.DataFrame(index = animal_prods_list + ["Dairy", "Fish, Seafood", "Byproducts"], columns = data.columns.to_list())

        # main aquatic products (ie, fish and crustaceans)
        aquatic_products = comm_group(FAO_comm_groups, "Fish, Seafood")["Item"].to_list() + ["Fish, Liver Oil", "Fish, Body Oil"]
        fish_supply = data.iloc[data.index.get_level_values("Item").isin(aquatic_products)]
        animal.loc["Fish, Seafood"] = np.sum(fish_supply, axis = 0)
        # handle additional watery products
        temp_sum = pd.DataFrame(columns = data.columns.to_list())
        try:
            temp_sum = pd.concat([temp_sum, data.xs("Aquatic Animals, Others", level = "Item")])
        except KeyError:
            None
        try:
            temp_sum = pd.concat([temp_sum, data.xs("Aquatic Plants", level = "Item")])
        except KeyError:
            None
        try:
            temp_sum = pd.concat([temp_sum, data.xs("Meat, Aquatic Mammals", level = "Item")])
        except KeyError:
            None
        animal.loc["Fish, Seafood"] += np.sum(temp_sum, axis = 0)

        # remove aq prods from animal prod data
        mask = np.logical_not(data.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Fish, Seafood")["Item"].to_list()\
                                + ["Aquatic Animals, Others", "Meat, Aquatic Mammals", "Aquatic Plants", "Fish, Liver Oil", "Fish, Body Oil"]))
        data = data[mask]

        # animal products
        for item in animal_prods_list:
            try:
                animal.loc[item] = data.xs(item, level = "Item").values[0]
            except KeyError:
                animal.loc[item] = 0
                error_rep(item)

        # remove meats
        mask = np.logical_not(data.index.get_level_values("Item").isin(animal_prods_list))
        data = data[mask]

        # dairy products
        dairy_sum = pd.DataFrame(index = dairy, columns = data.columns.to_list())
        for item in dairy:
            try:
                supply = data.xs(item, level = "Item").values[0]
            except KeyError:
                supply = 0
            dairy_sum.loc[item] = supply
        animal.loc["Dairy"] = np.sum(dairy_sum, axis = 0)

        # remove dairy products
        mask = np.logical_not(data.index.get_level_values("Item").isin(dairy))
        data = data[mask]

        supply = data
        animal.loc["Byproducts"] = np.sum(supply, axis = 0)

        return animal



    vegetal_commodity_production_5 = pd.DataFrame(columns = staple_crops \
                                                + vegetal_prods_grouped_list \
                                                + ["Luxuries (excluding Alcohol)", "Alcohol"] \
                                                + ["Other"],
                                                index = area_index.index)

    animal_commodity_production_5 = pd.DataFrame(columns = animal_prods_list \
                                                + ["Dairy", "Fish, Seafood", "Byproducts"],
                                                index = area_index.index)

    vegetal_commodity_production_ratios = pd.DataFrame(columns = staple_crops \
                                                + vegetal_prods_grouped_list \
                                                + ["Luxuries (excluding Alcohol)", "Alcohol"] \
                                                + ["Other"],
                                                index = area_index.index)

    animal_commodity_production_ratios = pd.DataFrame(columns = animal_prods_list \
                                                + ["Dairy", "Fish, Seafood", "Byproducts"],
                                                index = area_index.index)


    for continent in area_index.Continent.unique():
        for region in area_index[area_index.Continent == continent].Region.unique():
            FBS = io.load(f"data\\{continent}\\{region}", f"FoodBalanceSheets_E_{region}")
            for area in area_index[area_index.Region == region].index.to_list():

                FBS_area_dat = FBS.xs(area, level = "Area")

                vegetal_production = veggies(FBS_area_dat, continent, region, area)
                animal_production = animals(FBS_area_dat, continent, region, area)

                def plot():
                    plotlist = ["BRAZIL", "UNITEDSTATESOFAMERICA", "INDIA"]
                    if area in plotlist:
                        plt.xlabel("Year")
                        plt.ylabel("Production (1000 Tonnes)")
                        plt.plot(vegetal_production.T)
                        plt.legend(vegetal_production.T)
                        plt.xticks(vegetal_production.T.index.to_list()[9::10])
                        plt.show()
                #plot()

                vegetal_commodity_production_5.loc[area] = vegetal_production.iloc[:, :-5].mean(axis = 1)
                animal_commodity_production_5.loc[area] = animal_production.iloc[:, :-5].mean(axis = 1)
                pd.set_option("display.max_rows", None)

    for col in vegetal_commodity_production_ratios:
        vegetal_commodity_production_ratios[col] = vegetal_commodity_production_5[col] / np.sum(vegetal_commodity_production_5[col])
    for col in animal_commodity_production_ratios:
        animal_commodity_production_ratios[col] = animal_commodity_production_5[col] / np.sum(animal_commodity_production_5[col])

    io.save("lib\\dat\\production", "vegetal_commodity_production_ratios", vegetal_commodity_production_ratios)
    io.save("lib\\dat\\production", "animal_commodity_production_ratios", animal_commodity_production_ratios)
