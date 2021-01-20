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


def main(continent, region, area, path):


    energy_density = lib.dat.livestock_params.energy_density
    conversion_efficiency = lib.dat.livestock_params.conversion_efficiency
    byproduct_feed_potential = lib.dat.livestock_params.byproduct_feed_potential

    fed_without_forage_ratio= io.load(path, f"livestock\\fed_without_forage_{area}") # correct - production level
    # processing occurs in country - as does distribution
    waste_energy_available_area = io.load(path, f"food_waste\\vegetal_waste_energy_produced_{area}")
    food_energy_for_human_animal_production = io.load(path, f"production\\production_energy_for_human_animal_{area}")
    idx = food_energy_for_human_animal_production.index.to_list()

    fed_without_forage_meat_energy = pd.DataFrame(index=idx[:-2], columns=food_energy_for_human_animal_production.columns.to_list())  # MJ/year
    forage_fed_meat_energy = pd.DataFrame(index=idx[:-2], columns=food_energy_for_human_animal_production.columns.to_list())  # MJ/year
    fed_without_forage_meat_mass = pd.DataFrame(index=idx[:-2], columns=food_energy_for_human_animal_production.columns.to_list())  # kg(meat)/year
    fed_without_forage_feed_demand_mass = pd.DataFrame(index=idx[:-2], columns=food_energy_for_human_animal_production.columns.to_list())  # kg(feed)/year
    fodder_and_residues_feed_demand_energy = pd.DataFrame(index=idx[:-2], columns=food_energy_for_human_animal_production.columns.to_list())  # MJ/year

    for item in fed_without_forage_meat_mass.index.to_list():

        # #################################################################################################
        fed_without_forage_meat_energy.loc[item] = food_energy_for_human_animal_production.loc[item].values * fed_without_forage_ratio.loc[item].values  # MJ/year

        forage_fed_meat_energy.loc[item] = food_energy_for_human_animal_production.loc[item].values * (1 - fed_without_forage_ratio.loc[item]).values  # MJ/year

        fed_without_forage_meat_mass.loc[item] = fed_without_forage_meat_energy.loc[item] * (1 / energy_density[item])  # kg(meat)/year

        fodder_and_residues_feed_demand_energy.loc[item] = fed_without_forage_meat_energy.loc[item] / conversion_efficiency[item]

        # subtract energy available from post-production waste
        split = byproduct_feed_potential[item][1]\
                / ( byproduct_feed_potential["Bovine Meat"][1]\
                + byproduct_feed_potential["Poultry Meat"][1]\
                + byproduct_feed_potential["Pigmeat"][1]\
                + byproduct_feed_potential["Mutton & Goat Meat"][1]\
                + byproduct_feed_potential["Dairy"][1]\
                + byproduct_feed_potential["Eggs"][1] )

        potential = byproduct_feed_potential[item][1] * fodder_and_residues_feed_demand_energy.loc[item]
        potential = [x if x > 0 else 0 for x in potential]
        actual = waste_energy_available_area.loc["post_production_to_feed"] * split # re-visit this
        used = np.where(actual > potential, potential, actual)
        fodder_and_residues_feed_demand_energy.loc[item] = fodder_and_residues_feed_demand_energy.loc[item] - used

    io.save(f"{path}\\livestock", f"feed_demand_energy_minus_post_prod_{area}", fodder_and_residues_feed_demand_energy)
    io.save(f"{path}\\livestock", f"forage_feed_energy_{area}", forage_fed_meat_energy)
