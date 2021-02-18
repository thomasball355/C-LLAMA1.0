import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stat
import math
import os
import re
from matplotlib.lines import Line2D
from matplotlib import cm
from matplotlib import colors as mpl_col
import seaborn as sns

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation



def main(continent, region, area, path):

    regional_maximum_yields = io.load(f"{path}\\yield_production", "regional_maximum_yields")
    regional_minimum_yields = io.load(f"{path}\\yield_production", "regional_minimum_yields")
    data = io.load(f"{path}\\yield_production", f"yield_hist_{area}")

    output_data = pd.DataFrame(columns = np.arange(2013, 2051, 1), index = data.index)
    def line(dat, dat_start, dat_end):
        years = np.arange(dat_start, dat_end + 1, 1)
        line_params = stat.linregress(years, dat)
        return line_params
    max_list = {}

    for crop in data.index.to_list():

        years = 20
        line_params = line(data.loc[crop].astype(float).iloc[-years:], 2018 - years, 2017)

        slope = line_params[0]
        intercept = line_params[1]
        r = line_params[2]
        p = line_params[3]

        lin = lambda x: (x * slope) + intercept
        val_2050 = lin(2050)
        lin2 = lambda x: data.loc[crop].astype(float).iloc[-5:].mean() + (x - 2013) * ((val_2050 - data.loc[crop].astype(float).iloc[-5:].mean()) / (2050 - 2013))
        regional_max = regional_maximum_yields.loc[crop]
        regional_min = regional_minimum_yields.loc[crop]

        if r**2 > 0.2 and p < 0.05 and slope > 0:
            output_data.loc[crop] = [regional_min if lin2(x) < regional_min else regional_max if lin2(x) > regional_max else lin2(x) for x in output_data.columns.to_list()]
        else:
            output_data.loc[crop] = data.loc[crop].astype(float).iloc[-5:-1].mean()

        if np.sum(data.loc[crop]) > 0:
            max_list[crop] = regional_max

    io.save(f"{path}\\yield_production", f"yield_projection_{area}", output_data)

    def plot():

        def col_rand(a, b):
            col = [np.random.randint(a, b)/100, np.random.randint(a, b)/100, np.random.randint(a, b)/100]
            return col

        area_list = ["INDIA", "CHINAMAINLAND", "UNITEDSTATESOFAMERICA", "BELIZE", "BRAZIL", "FRANCE"]

        if area in area_list:

            palette = ["#2571FF", "#FF7826", "#FF3325", "#CC2F5F", "#81525A", "#777750", "#51512B", "#5AFF58", "#1FDBFC", "#545557", "#81D517"]

            croplist = ["Sugar cane",
                        "Maize and products",
                        "Rice (Milled Equivalent)",
                        "Wheat and products",
                        "Palm Oil",
                        "Soyabeans",
                        "Potatoes and products",
                        "Cassava and products",
                        "Cereals - Excluding Beer",
                        "Fruits - Excluding Wine",
                        "Vegetables"]

            print(f"Plotting {area}")
            colours = lib.dat.colours.vegetal_prods
            print(data)

            custom_lines = []

            plt.style.use("Solarize_Light2")

            list = []
            i = 0
            for crop in croplist:

                color = col_rand(0, 80)
                if np.sum(data.loc[crop]) > 0:

                    custom_lines.append(Line2D([0], [0], color = palette[i], lw = "3"))

                    list.append(crop)

                    plt.plot(np.arange(1961, 2017+1, 1), data.loc[crop].astype(float), marker = "x", linewidth = 0, color = palette[i], label = crop)

                    plt.plot(output_data.loc[crop].astype(float), color = palette[i])

                    plt.plot(2050, max_list[crop], color = palette[i], marker = "^", markersize = 10)
                    i += 1

            plt.ylabel("Yield (tonnes/ha)")
            plt.xlabel("Year")
            plt.xticks(np.arange(1960, 2051, 10))
            plt.xlim(1961, 2051)
            plt.legend(custom_lines, list)
            plt.show()
    #plot()
