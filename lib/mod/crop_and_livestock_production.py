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

    vegetal_commodity_production_ratios = io.load("lib\\dat\\production", "vegetal_commodity_production_ratios")
    animal_commodity_production_ratios = io.load("lib\\dat\\production", "animal_commodity_production_ratios")

    vegetal_production_required = pd.DataFrame( index = vegetal_commodity_production_ratios.columns,
                                                columns = np.arange(2013, 2051, 1), data = 0)
    animal_production_required = pd.DataFrame( index = animal_commodity_production_ratios.columns,
                                                columns = np.arange(2013, 2051, 1), data = 0)

    for continent in area_index.Continent.unique():
        for region in area_index[area_index.Continent == continent].Region.unique():
            for area in area_index[area_index.Region == region].index.to_list():

                area_production_vegetal = pd.DataFrame( index = vegetal_production_required.index,
                                                columns = vegetal_production_required.columns)

                production_energy_for_human = io.load(  f"data\\{continent}\\{region}\\food_supply",
                                                        f"production_energy_for_human_{area}")

                PEfH_V = production_energy_for_human.xs("Vegetal Products",
                                                        level = "Group").xs("MJ/year",
                                                        level = "Unit")
                PEfH_V.index.name = None

                PEfH_A = production_energy_for_human.xs("Animal Products",
                                                        level = "Group").xs("MJ/year",
                                                        level = "Unit")
                PEfH_A.index.name = None

                vegetal_production_required = vegetal_production_required.add(PEfH_V.values,
                                                                                fill_value = 0)

                animal_production_required = animal_production_required.add(PEfH_A.values,
                                                                                fill_value = 0)


    crop_properties = pd.read_excel("lib\\dat\\vegetal_product_properties.xlsx", index_col = 0)
    animal_properties = pd.read_excel("lib\\dat\\animal_product_properties.xlsx", index_col = 0)

    for continent in area_index.Continent.unique():
        for region in area_index[area_index.Continent == continent].Region.unique():
            for area in area_index[area_index.Region == region].index.to_list():
                area_multiplier_vegetal = vegetal_commodity_production_ratios.loc[area]
                area_multiplier_animal = animal_commodity_production_ratios.loc[area]
                area_production_vegetal =   (vegetal_production_required.T \
                                            * area_multiplier_vegetal).T #energy MJ/year
                area_production_animal =    (animal_production_required.T \
                                            * area_multiplier_animal).T #energy MJ/year
                crop_properties = crop_properties[np.logical_not(crop_properties.index.isin(["Sugar cane", "Sugar Crops"]))]
                area_production_vegetal_mass = (area_production_vegetal.T / crop_properties["energy_density"]).T # kilograms
                area_production_animal_mass = (area_production_animal.T / animal_properties["energy_density"]).T #
                path = f"data\\{continent}\\{region}\\production"
                io.save(path, f"production_energy_for_human_vegetal_{area}", area_production_vegetal)
                io.save(path, f"production_mass_vegetal_for_human_{area}", area_production_vegetal_mass)
                io.save(path, f"production_energy_for_human_animal_{area}", area_production_animal)
                io.save(path, f"production_mass_animal_for_human_{area}", area_production_animal_mass)
