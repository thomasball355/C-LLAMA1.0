import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.stats as stat

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.dat.colours
import lib.dat.food_commodity_seperation
import model_params

desired_cals = model_params.desired_cals_target

def main(data, continent, region, area, path):

    total_fs = data.xs("Grand Total", level = "Item").xs("Food supply (kcal/capita/day)", level = "Element").values[0]

    val = lambda x:   ((x / desired_cals) - 0.5) / (0.7)
    # val2 = lambda x:    0.86 * (np.log(x / desired_cals)) + 0.86

    dev_metric_hist = [0.0 if val(x) < 0 else val(x) if val(x) <= 1.0 else 1.0 for x in total_fs]

    dev_hist = io.load("lib\\dat", "dev_met_hist")
    dev_hist.loc[area] = dev_metric_hist
    io.save("lib\\dat", f"dev_met_hist", dev_hist)

    def line(dat, years):
        line_params = stat.linregress(years, dat)
        return line_params

    line_vars = line(dev_metric_hist[-25:-1], np.arange(2013 + 1 - 24, 2013 + 1, 1))
    slope       = line_vars[0]
    intercept   = line_vars[1]
    r           = line_vars[2]
    p           = line_vars[3]

    lin = lambda x: x * slope + intercept
    hist_mean = np.mean(dev_metric_hist[-5:])

    def linear_interpolate():
        val_2050 = lin(2050)
        val_2013 = float(dev_metric_hist[-1])
        diff = val_2050 - val_2013
        if r**2 > 0.2 and p < 0.05:
            if 0.0 < slope < 0.020:
                new_line = lambda x: val_2013 + ((x - 2013) * (diff/(2050 - 2013)))
                dev_metric_proj = [0.0 if new_line(x) <= 0.0 else new_line(x) if new_line(x) <= 1.0 else 1.0 for x in range(2013, 2051)]
            else:
                dev_metric_proj = [0.0 if hist_mean <= 0.0 else hist_mean if hist_mean <= 1.0 else 1.0 for x in range(2013, 2051)]
        else:
            dev_metric_proj = [0.0 if hist_mean <= 0.0 else hist_mean if hist_mean <= 1.0 else 1.0 for x in range(2013, 2051)]
        return dev_metric_proj

    dev_metric_proj = linear_interpolate()

    def plot():
        #area_list = ["CHINAMAINLAND", "UNITEDSTATESOFAMERICA", "NIGER", "BELIZE", "BRAZIL", "JAPAN", "UNITEDKINGDOM", "NIGERIA", "INDIA", "AUSTRALIAANDNEWZEALAND", "CONGO", "ETHOPIA", "CHAD"]
        if area in area_list:
            plt.plot(np.arange(1961, 2013 + 1, 1), dev_metric_hist, marker = "x", linewidth = "0")
            plt.plot(np.arange(2013, 2051, 1), dev_metric_proj)
            plt.xlabel("Year")
            plt.ylabel("Metric")
            plt.ylim(0.0, 1.1)
            plt.xticks(np.arange(1960, 2051, 10))
            plt.show()
    #plot()

    io.save(f"{path}\\dev_metrics", f"dev_metric_{area}", dev_metric_proj)
