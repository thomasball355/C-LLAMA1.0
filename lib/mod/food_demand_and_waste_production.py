import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation
import lib.dat.livestock_params
import lib.dat.constants as cn

def main(continent, region, area, path):
    try:

        animal_processing_losses = lib.dat.livestock_params.animal_processing_losses

        food_supply     = io.load(f"{path}\\food_supply", f"FoodsupplyProjection_{area}")
        waste_ratios    = io.load(f"{path}\\food_waste", f"waste_ratios_{area}")
        population      = io.load("lib\\dat\\population", "SSP2_population_trajectory_interpolated").loc[area] * 1E+06

        food_supply_calories        = food_supply.xs("Food supply (kcal/capita/day)", level = "Data")
        food_supply_energy_vegetal  = food_supply.xs("Energy Contribution", level = "Data").xs("Vegetal Products", level = "Element")
        food_supply_energy_animal   = food_supply.xs("Energy Contribution", level = "Data").xs("Animal Products", level = "Element")

        waste_energy_produced_vegetal = pd.DataFrame(index = ["post_production", "processing", "distribution", "post_production_to_feed"],
                                                     columns = food_supply_energy_vegetal.columns)
        production_for_human_vegetal = pd.DataFrame(index = food_supply_energy_vegetal.index,
                                                    columns = food_supply_energy_vegetal.columns)
        production_for_human_animal = pd.DataFrame(index = food_supply_energy_animal.index,
                                                    columns = food_supply_energy_animal.columns)

        for col in production_for_human_vegetal:

            production_for_human_vegetal[col]   = population[col] * cn.days_in_year * cn.megajoule_in_kcal\
                                                * (food_supply_energy_vegetal[col]\
                                                / (1 - (waste_ratios.loc["processing"][col]\
                                                + waste_ratios.loc["distribution"][col])))

            production_for_human_animal[col]    = population[col] * cn.days_in_year * cn.megajoule_in_kcal\
                                                * (food_supply_energy_animal[col]\
                                                / (1 - (animal_processing_losses\
                                                + waste_ratios.loc["distribution"][col])))

            waste_energy_produced_vegetal.loc["distribution"][col]  = np.sum(production_for_human_vegetal[col])\
                                                                    * waste_ratios.loc["distribution"][col]
            waste_energy_produced_vegetal.loc["processing"][col]    = np.sum(production_for_human_vegetal[col])\
                                                                    * waste_ratios.loc["processing"][col]
            waste_energy_produced_vegetal.loc["post_production"][col]   = np.sum(production_for_human_vegetal[col])\
                                                                        * waste_ratios.loc["post_production"][col]

        waste_energy_produced_vegetal.loc["post_production_to_feed"]    = waste_energy_produced_vegetal.loc["post_production"]\
                                                                        * waste_ratios.loc["post_production_to_feed"].values

        production_for_human_animal.index = production_for_human_animal.index.set_levels(["MJ/year"], level = 1)
        production_for_human_vegetal.index = production_for_human_vegetal.index.set_levels(["MJ/year"], level = 1)

        production_energy_for_human = pd.concat([production_for_human_vegetal, production_for_human_animal], axis = 0)

        index_labels = [["Vegetal Products" for x in production_for_human_vegetal.index.to_list()]\
                        + ["Animal Products" for x in production_for_human_animal.index.to_list()],
                        [x[0] for x in production_for_human_vegetal.index.to_list()]\
                        + [x[0] for x in production_for_human_animal.index.to_list()],
                        ["MJ/year" for x in production_for_human_vegetal.index.to_list() + production_for_human_animal.index.to_list()]]

        production_energy_for_human.index = pd.MultiIndex.from_arrays(index_labels, names = ["Group", "Item", "Unit"])

        io.save(f"{path}\\food_supply", f"production_energy_for_human_{area}", production_energy_for_human)
        io.save(f"{path}\\food_waste", f"vegetal_waste_energy_produced_{area}", waste_energy_produced_vegetal)

        # WES_reg     = io.load(f"data\\{continent}\\{region}", f"_waste_energy_sums_regional_temp")
        # WES_cont    = io.load(f"data\\{continent}", f"_waste_energy_sums_continent_temp")
        # WES_global  = io.load(f"data", f"_waste_energy_sums_global_temp")
        # WES_reg    = WES_reg + waste_energy_produced_vegetal
        # WES_cont   = WES_cont + waste_energy_produced_vegetal
        # WES_global  = WES_global + waste_energy_produced_vegetal
        # io.save(f"data\\{continent}\\{region}", f"_waste_energy_sums_regional_temp", WES_reg)
        # io.save(f"data\\{continent}", f"_waste_energy_sums_continent_temp", WES_cont)
        # io.save(f"data", f"_waste_energy_sums_global_temp", WES_global)

    except KeyError:
        print(f"No calculations made for {area}: re-address.")
