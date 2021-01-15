import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation



def main(continent, region, area, path):

    harvest_factor = pd.read_csv("lib\\dat\\harvest_residues\\harvest_factors_krausmann2008.csv", index_col = 0)
    recovery_factor = pd.read_csv("lib\\dat\\harvest_residues\\recovery_factors_krausmann2008.csv", index_col = 0)

    production_mass_vegetal_for_human = io.load(path, f"production\\production_mass_vegetal_for_human_{area}")
    production_mass_animal_for_human = io.load(path, f"production\\production_mass_animal_for_human_{area}")

    # dict to convert into areas listed in data
    area_dict = {"NORTHERNAMERICA": "North America",
                 "SOUTHAMERICA": "Latin America",
                 "CENTRALAMERICA": "Latin America",
                 "CARIBBEAN": "Latin America",
                 "EASTERNAFRICA": "Sub Saharan Africa",
                 "WESTERNAFRICA": "Sub Saharan Africa",
                 "NORTHERNAFRICA": "North Africa and West Asia",
                 "SOUTHERNAFRICA": "Sub Saharan Africa",
                 "MIDDLEAFRICA": "Sub Saharan Africa",
                 "CENTRALASIA": "Central and Southern Asia",
                 "EASTERNASIA": "East and South-East Asia",
                 "SOUTHEASTERNASIA": "East and South-East Asia",
                 "SOUTHERNASIA": "Central and Southern Asia",
                 "WESTERNASIA": "North Africa and West Asia",
                 "EASTERNEUROPE": "Europe",
                 "WESTERNEUROPE": "Europe",
                 "NORTHERNEUROPE": "Europe",
                 "SOUTHERNEUROPE": "Europe",
                 "AUSTRALIAANDNEWZEALAND": "Oceania",
                 "MICRONESIA": "Oceania",
                 "POLYNESIA": "Oceania",
                 "MELANESIA": "Oceania"
                 }

    harvest_factor_region = harvest_factor[area_dict[region]]

    # for item in harvest_factor_region:
    #     if item <= 0.0:
    #         harvest_factor_region[item] = 0

    potential_residues = (production_mass_vegetal_for_human.T * harvest_factor_region).T

    # dict to convert into areas listed in data
    area_dict_2 = {"NORTHERNAMERICA": "N. America Oceania",
                 "SOUTHAMERICA": "Latin America",
                 "CENTRALAMERICA": "Latin America",
                 "CARIBBEAN": "Latin America",
                 "EASTERNAFRICA": "Subsaharan Africa",
                 "WESTERNAFRICA": "Subsaharan Africa",
                 "NORTHERNAFRICA": "N. Africa W. Asia",
                 "SOUTHERNAFRICA": "Subsaharan Africa",
                 "MIDDLEAFRICA": "Subsaharan Africa",
                 "CENTRALASIA": "S. and C. Asia",
                 "EASTERNASIA": "E. Asia",
                 "SOUTHEASTERNASIA": "E. Asia",
                 "SOUTHERNASIA": "S. and C. Asia",
                 "WESTERNASIA": "N. Africa W. Asia",
                 "EASTERNEUROPE": "E. Europe",
                 "WESTERNEUROPE": "W. Europe",
                 "NORTHERNEUROPE": "W. Europe",
                 "SOUTHERNEUROPE": "E. Europe",
                 "AUSTRALIAANDNEWZEALAND": "N. America Oceania",
                 "MICRONESIA": "N. America Oceania",
                 "POLYNESIA": "N. America Oceania",
                 "MELANESIA": "N. America Oceania"
                 }

    produced_residues = (potential_residues.T * recovery_factor[area_dict_2[region]]).T

    io.save(f"{path}\\harvest_residues", f"harvest_residues_recovered_{area}", produced_residues)
