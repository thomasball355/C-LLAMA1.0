import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation

def main(data, continent, region, path):

    regional_max    = data[0].max(axis = 0)
    regional_min    = data[1].min(axis = 0)
    production      = data[2]

    for col in production:
        production[col] = production[col] / np.sum(production[col])

    io.save(f"{path}\\yield_production", "regional_maximum_yields", regional_max)
    io.save(f"{path}\\yield_production", "regional_minimum_yields", regional_min)
    io.save(f"{path}\\yield_production", "crop_production_ratio", production)
