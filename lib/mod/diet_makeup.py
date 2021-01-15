import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation

import model_params
############# List of variables here for now #####

# desired calories for 2050 (pre_post_prod)
desired_cals = model_params.desired_cals_target / 1.3
dev_target_year = model_params.dev_target_year

# modify final value of animal_product contribution to diet
veg_change              = model_params.veg_change
non_dairy_animal_change = model_params.non_dairy_animal_change

##################################################


def main(data, continent, region, area, path):

    post_consumer_waste = io.load(f"{path}\\food_waste", f"waste_ratios_{area}").loc["post_production"]

    def diet_makeup(data, continent, region, area, path, desired_cals, post_consumer_waste, veg_change, non_dairy_animal_change):

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

        def commodities(data, continent, region, area):

            # list of grouped commodities as defined by FAO
            FAO_comm_groups = pd.read_csv(f"data\\FAOSTAT_data_11-6-2019_commoditygroups.csv")
            # dat is total food supply data for a continent (or country), based on input "data"
            dat = data.xs("Food supply (kcal/capita/day)", level = "Element")

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

            # split data into animal and vegetal products
            vegetal_dat = dat.iloc[dat.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Vegetal Products")["Item"])]
            animal_dat = dat.iloc[dat.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Animal Products")["Item"])]

            # housekeeping, to check what's left over
            mask = np.logical_not(dat.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Vegetal Products")["Item"]))
            dat = dat[mask]
            mask = np.logical_not(dat.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Animal Products")["Item"]))
            dat = dat[mask]

            # create dataframes for output
            vegetal = pd.DataFrame(index = staple_crops + vegetal_prods_grouped_list + ["Luxuries (excluding Alcohol)", "Alcohol"] + ["Other"], columns = dat.columns.to_list())
            animal = pd.DataFrame(index = animal_prods_list + ["Dairy", "Fish, Seafood", "Byproducts"], columns = dat.columns.to_list())

            # population data, summed population for the continent, population weighting for calculating means
            population = data.xs("Population", level = "Item")
            population_sum = np.sum(population, axis = 0)
            pop_weight = population/population_sum


            # Vegetal products
            def veggies(data, continent, region, area):

                # key crops have their own trajectory
                for crop in staple_crops:
                    try:
                        crop_supp = data.xs(crop, level = "Item")
                        try:
                            running_sum = pd.DataFrame(index = crop_supp.index.get_level_values("Area"), columns = crop_supp.columns.to_list())
                            for area in crop_supp.index.get_level_values("Area"):
                                crop_lis = crop_supp.xs(area, level = "Area")
                                running_sum.loc[area] = crop_lis.values
                        except KeyError:
                            running_sum = crop_supp.values
                        vegetal.loc[crop] = np.sum(running_sum, axis = 0)
                    except KeyError:
                        error_rep(crop)

                # remove key crop groups so they don't get included in the aggregated groups
                mask = np.logical_not(data.index.get_level_values("Item").isin(staple_crops + ["Sugar cane", "Sugar beet"]))
                data = data[mask]


                # aggregated crop groups
                for group in vegetal_prods_grouped_list:
                    item_list = comm_group(FAO_comm_groups, group)["Item"]
                    item_list = [x for x in item_list if x not in staple_crops]
                    try:
                        group_dat = data.iloc[data.index.get_level_values("Item").isin(item_list)].sum(level = "Area")
                        running_sum = pd.DataFrame(index = group_dat.index.get_level_values("Area"), columns = group_dat.columns.to_list())
                        for area in group_dat.index.get_level_values("Area").to_list():
                            running_sum.loc[area] = group_dat.xs(area).values
                    except KeyError:
                        group_dat = data.iloc[data.index.get_level_values("Item").isin(item_list)]
                        running_sum = group_dat

                    vegetal.loc[group] = np.sum(running_sum, axis = 0)
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
                        food_supp = data.xs(food, level = "Item")
                    except KeyError:
                        error_rep(food)
                    try:
                        running_sum = pd.DataFrame(index = group_dat.index.get_level_values("Area"), columns = group_dat.columns.to_list())
                        for area in group_dat.index.get_level_values("Area").to_list():
                            try:
                                running_sum.loc[area] = food_supp.xs(area).values
                            except KeyError:
                                error_rep(food)
                    except KeyError:
                        running_sum = food_supp
                    luxuries_sum.loc[food] = np.sum(running_sum, axis = 0)
                vegetal.loc["Luxuries (excluding Alcohol)"] = np.sum(luxuries_sum, axis = 0)
                mask = np.logical_not(data.index.get_level_values("Item").isin(luxuries))
                data = data[mask]


                alcohol_sum = pd.DataFrame(index = alcohol, columns = data.columns.to_list())
                for drink in alcohol:
                    try:
                        supp = data.xs(drink, level = "Item")
                    except KeyError:
                        supp = 0
                        error_rep(drink)
                    try:
                        running_sum = pd.DataFrame(index = group_dat.index.get_level_values("Area"), columns = group_dat.columns.to_list())
                        for area in group_dat.index.get_level_values("Area").to_list():
                            try:
                                running_sum.loc[area] = supp.xs(area).values
                            except KeyError:
                                error_rep(drink)
                    except KeyError:
                        running_sum = supp
                    alcohol_sum.loc[drink] = np.sum(running_sum, axis = 0)
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
                    food_supp = data.xs(item, level = "Item")
                    try:
                        running_sum = pd.DataFrame(index = group_dat.index.get_level_values("Area"), columns = group_dat.columns.to_list())
                        for area in running_sum.index.get_level_values("Area").to_list():
                            try:
                                running_sum.loc[area] = np.mean(food_supp.xs(area).values, axis = 0)
                            except KeyError:
                                error_rep(item)
                    except KeyError:
                        running_sum = food_supp

                    misc_running_sum.loc[item] = np.sum(running_sum.values[0], axis = 0)

                vegetal.loc["Other"] = np.sum(misc_running_sum, axis = 0)

                return

            veggies(vegetal_dat, continent, region, area)

            # Animal products
            def animals(data, continent, region, area):

                def aquatic_products():

                    # main aquatic products (ie, fish and crustaceans)
                    aquatic_products = comm_group(FAO_comm_groups, "Fish, Seafood")["Item"].to_list() + ["Fish, Liver Oil", "Fish, Body Oil"]
                    try:
                        fish_supply = data.iloc[data.index.get_level_values("Item").isin(aquatic_products)].sum(level = "Area")
                    except KeyError:
                        fish_supply = data.iloc[data.index.get_level_values("Item").isin(aquatic_products)]
                    weighted = fish_supply
                    animal.loc["Fish, Seafood"] = np.sum(weighted, axis = 0)

                    # handle additional watery products
                    try:
                        temp_sum = pd.DataFrame(columns = data.columns.to_list(), index = data.index.get_level_values("Area"))
                        for area in data.index.get_level_values("Area"):
                            try:
                                temp_sum.loc[area] = data.loc["Aquatic Animals, Others"].loc[area]
                            except KeyError:
                                None
                            try:
                                temp_sum.loc[area] += data.loc["Aquatic Plants"].loc[area]
                            except KeyError:
                                None
                    except KeyError:
                        temp_sum = pd.DataFrame(columns = data.columns.to_list())
                        try:
                            temp_sum    = data.loc["Aquatic Animals, Others"]
                        except KeyError:
                            None
                        try:
                            try:
                                temp_sum    += data.loc["Aquatic Plants"]
                            except ValueError:
                                None # This is a bit sketchy
                        except KeyError:
                            None
                    animal.loc["Fish, Seafood"] += np.sum(temp_sum, axis = 0)

                    return
                aquatic_products()

                # remove aq prods from animal prod data
                mask = np.logical_not(data.index.get_level_values("Item").isin(comm_group(FAO_comm_groups, "Fish, Seafood")["Item"].to_list()\
                                        + ["Aquatic Animals, Others", "Aquatic Plants", "Fish, Liver Oil", "Fish, Body Oil"]))
                data = data[mask]


                # animal products
                def meat():

                    for item in animal_prods_list:
                        try:
                            supply = data.xs(item, level = "Item").mean(level = "Area")
                            running_sum = pd.DataFrame(index = supply.index.get_level_values("Area").to_list(), columns = supply.columns.to_list())
                            for area in supply.index.get_level_values("Area").to_list():
                                running_sum.loc[area] = supply.loc[area].values
                            animal.loc[item] = np.sum(running_sum, axis = 0)
                        except KeyError:
                            try:
                                running_sum = data.xs(item, level = "Item").mean(level = "Unit")
                            except KeyError:
                                error_rep(item)
                        animal.loc[item] = np.sum(running_sum, axis = 0)
                    return
                meat()

                # remove meats
                mask = np.logical_not(data.index.get_level_values("Item").isin(animal_prods_list))
                data = data[mask]


                # dairy products
                def dairy_products(area):

                    # annoyingly have to iterate because milk is included twice in the
                    # data (once as a 'group' that includes only itself).
                    dairy_sum = pd.DataFrame(index = dairy, columns = data.columns.to_list())
                    for item in dairy:
                        try:
                            supply = data.xs(item, level = "Item").mean(level = "Area")
                            running_sum = pd.DataFrame(index = supply.index.get_level_values("Area").to_list(), columns = supply.columns.to_list())
                            for area in supply.index.get_level_values("Area").to_list():
                                running_sum.loc[area] = supply.loc[area].values
                        except KeyError:
                            try:
                                running_sum = data.xs(item, level = "Item").mean(level = "Unit")
                            except KeyError:
                                error_rep(item)
                        dairy_sum.loc[item] = np.sum(running_sum, axis = 0)
                    animal.loc["Dairy"] = np.sum(dairy_sum, axis = 0)
                    return
                dairy_products(area)

                # remove dairy products
                mask = np.logical_not(data.index.get_level_values("Item").isin(dairy))
                data = data[mask]


                def byprods():

                    try:
                        supply = data.sum(level = "Area")
                    except KeyError:
                        supply = data
                    weighted = supply * pop_weight.values
                    animal.loc["Byproducts"] = np.sum(weighted, axis = 0)
                    return

                byprods()


                return

            animals(animal_dat, continent, region, area)


            vegetal_ratio = lib.funcs.perc_contributions_WRAP.historic_ratio(vegetal)
            animal_ratio = lib.funcs.perc_contributions_WRAP.historic_ratio(animal)

            vegetal_ratio_projection = lib.funcs.perc_contributions_WRAP.percentage_contributions(vegetal_ratio, 2050, 1961, 2013)
            animal_ratio_projection = lib.funcs.perc_contributions_WRAP.percentage_contributions(animal_ratio, 2050, 1961, 2013)

            vegetal_ratio_projection = vegetal_ratio_projection.astype("float64")
            animal_ratio_projection = animal_ratio_projection.astype("float64")


            # FINISH THIS (not yet)
            # def plot():
            #     #matplotlib is stupid >:(
            #     def matplotlibisstupid(data):
            #         plotted = pd.DataFrame(columns = data.columns.to_list())
            #         plotdat = []
            #         for row in data.index:
            #             if np.nansum(data.loc[row]) != 0:
            #                 plotted = plotted.append(data.loc[row])
            #             else:
            #                 print(f"Check: {row} missing or zero in {area} data")
            #         return plotted
            #
            #
            #     def plots(data, colour_set):
            #         plot_dat = matplotlibisstupid(data)
            #         cols = []
            #         for item in plot_dat.index.to_list():
            #             cols.append(colour_set[item])
            #
            #         print(plot_dat)
            #         plt.stackplot(  #np.arange(2013, 2051, 1),
            #                         plot_dat)#,)
            #                         # colors = cols,
            #                         # labels = plot_dat.index.to_list(),
            #                         # alpha = 0.8)
            #         plt.legend(loc = "upper left", fancybox = True, framealpha = 0.5)
            #         plt.ylabel("Diet contribution ratio")
            #         plt.xlabel("Year")
            #         plt.xticks(np.arange(2010, 2051, 5))
            #         plt.xlim(2013, 2050)
            #         #plt.ylim(0, 1.1)
            #         plt.show()
            #     plots(vegetal_ratio_projection, lib.dat.colours.vegetal_prods)
            #     plots(animal_ratio_projection, lib.dat.colours.animal_prods)
            # plot()

            # vegetal_ratio_projection.T.plot.area()
            # plt.show()
            # animal_ratio_projection.T.plot.area()
            # plt.show()

            return vegetal_ratio_projection, animal_ratio_projection


        def diet_contributions(data, continent, region, area):

                # historic population
            population = data.xs("Population", level = "Item")

            population_sum = np.sum(population, axis = 0)
            food_supp = data.xs("Food supply (kcal/capita/day)", level = "Element")

                # population weighting for regional means
            pop_weight = population / population_sum

                # vegetal products food supply
            veg = food_supp.xs("Vegetal Products", level = "Item")
            veg_weighted = np.sum(veg * pop_weight.values, axis = 0)
                # animal product food supply
            anim = food_supp.xs("Animal Products", level = "Item")
            anim_weighted = np.sum(anim * pop_weight.values, axis = 0)
                # of which fish
            fish = food_supp.xs("Fish, Seafood", level = "Item")
            fish_weighted = np.sum(fish * pop_weight.values, axis = 0)

                # diet proportions of each for the region (weighted by population)
            veg_ratio = veg_weighted/(veg_weighted+ anim_weighted + fish_weighted)
            anim_ratio = (anim_weighted - fish_weighted) / (veg_weighted+ anim_weighted + fish_weighted)
            fish_ratio = fish_weighted / (veg_weighted + anim_weighted + fish_weighted)

                # calculate trajectory of ratios of veg/meat/fish
            diet_props = pd.DataFrame([veg_ratio, anim_ratio, fish_ratio], index = ["Vegetal Products", "Animal Products", "Fish"])
            diet_props_projection = lib.funcs.perc_contributions_WRAP.percentage_contributions(diet_props, 2050, 1961, 2013).astype(float)

                # 2013 food supply
            fs_2013 = np.sum([anim_weighted-fish_weighted,fish_weighted,veg_weighted], axis = 0)[-1]
                # use that and desired food supply in 2050 * consumer waste (2500kcal/day * 0.28 or w/e)
            food_supply_cap_projected = lib.funcs.foodsupply_trajectory.calories_trajectory(2013, 2050, fs_2013, desired_cals, dev_target_year, post_consumer_waste)

            return diet_props_projection, food_supply_cap_projected


        # COMMENT THIS MESS!
        diet_props_projection, food_supp_cap_project = diet_contributions(data, continent, region, area)
        vegetal_commodity_ratio, animal_commodity_ratio = commodities(data, continent, region, area)

        years = animal_commodity_ratio.columns.to_list()
        _dairy = [1.0 + (x - 2013)*((non_dairy_animal_change)/(2050 - 2013)) for x in years]
        _vegetal = [1.0 + (x - 2013)*((veg_change)/(2050 - 2013)) for x in years]

        animal_commodity_ratio.loc[animal_commodity_ratio.index != "Dairy"] = animal_commodity_ratio.loc[animal_commodity_ratio.index != "Dairy"].values / _dairy
        dairy_diff = np.sum([np.sum(animal_commodity_ratio.loc[animal_commodity_ratio.index != "Dairy"].values, axis = 0),
                            animal_commodity_ratio.loc[animal_commodity_ratio.index == "Dairy"].values], axis = 0)
        diet_props_projection.loc["Vegetal Products"] = diet_props_projection.loc["Vegetal Products"].values / dairy_diff * _vegetal

        for col in animal_commodity_ratio:
            animal_commodity_ratio[col] = animal_commodity_ratio[col] / np.sum(animal_commodity_ratio[col], axis = 0)
        for col in diet_props_projection:
            diet_props_projection[col] = diet_props_projection[col] / np.sum(diet_props_projection[col], axis = 0)

        arrays =    [["Vegetal Products" for x in vegetal_commodity_ratio.index.to_list()]\
                    + ["Animal Products" for x in animal_commodity_ratio.index.to_list()],
                    [x for x in vegetal_commodity_ratio.index.to_list()]\
                    + [x for x in animal_commodity_ratio.index.to_list()]
                    ]

        non_veg = np.sum([diet_props_projection.loc["Animal Products"].values, diet_props_projection.loc["Fish"].values], axis = 0)

        grand_diet_props = pd.DataFrame(vegetal_commodity_ratio * diet_props_projection.loc["Vegetal Products"].values, columns = vegetal_commodity_ratio.columns.to_list())
        grand_diet_props = pd.concat([grand_diet_props, animal_commodity_ratio * non_veg], axis = 0)

        grand_diet_energy = grand_diet_props * food_supp_cap_project.values

        grand_diet = pd.concat([grand_diet_energy, grand_diet_props, food_supp_cap_project, diet_props_projection])

        index_labels = [["Energy Contribution" for x in vegetal_commodity_ratio.index.to_list()]\
                        + ["Energy Contribution" for x in animal_commodity_ratio.index.to_list()]\
                        + ["Item Diet Proportions" for x in vegetal_commodity_ratio.index.to_list()]\
                        + ["Item Diet Proportions" for x in animal_commodity_ratio.index.to_list()]\
                        + ["Food supply (kcal/capita/day)"]\
                        + ["Group Diet Proportions"]*3,
                        ["Vegetal Products" for x in vegetal_commodity_ratio.index.to_list()]\
                        + ["Animal Products" for x in animal_commodity_ratio.index.to_list()]\
                        + ["Vegetal Products" for x in vegetal_commodity_ratio.index.to_list()]\
                        + ["Animal Products" for x in animal_commodity_ratio.index.to_list()]\
                        + ["Total Food Supply"]\
                        + ["Group Diet Proportions"]*3,
                        [x for x in vegetal_commodity_ratio.index.to_list()]\
                        + [x for x in animal_commodity_ratio.index.to_list()]\
                        + [x for x in vegetal_commodity_ratio.index.to_list()]\
                        + [x for x in animal_commodity_ratio.index.to_list()]\
                        + ["Food supply (kcal/capita/day)"]\
                        + ["Vegetal Products (ratio)", "Animal Products (ratio)", "Fish (ratio)"],
                        ["kcal/capita/day" for x in vegetal_commodity_ratio.index.to_list()]\
                        + ["kcal/capita/day" for x in animal_commodity_ratio.index.to_list()]\
                        + ["proportion" for x in vegetal_commodity_ratio.index.to_list()]\
                        + ["proportion" for x in animal_commodity_ratio.index.to_list()]\
                        + ["kcal/capita/day"]\
                        + ["proportion"]*3,
                        ]

        grand_diet.index = pd.MultiIndex.from_arrays(index_labels, names = ["Data", "Element", "Item", "Unit"])
        io.save(f"data\\{continent}\\{region}\\food_supply", f"FoodsupplyProjection_{area}", grand_diet)

        def plot_fs():
            area_list = ["CHINAMAINLAND", "UNITEDSTATESOFAMERICA", "BELIZE", "BRAZIL"]

            if area in area_list:
                print(grand_diet)
                grand_diet.xs("Food supply (kcal/capita/day)", level = "Data").T.plot()
                plt.show()
        #plot_fs()
    diet_makeup(data, continent, region, area, path, desired_cals, post_consumer_waste, veg_change, non_dairy_animal_change)
