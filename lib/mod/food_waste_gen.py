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

start_params        = model_params.waste_start_params

def main():

    years = np.arange(2013, 2051, 1)
    waste_ratios = pd.DataFrame(columns = years,
                                index = ["post_prod_low_dev", "post_prod_high_dev",
                                        "processing_low_dev", "processing_high_dev",
                                        "distribution_low_dev", "distribution_high_dev",
                                        "post_prod_to_feed_low_dev", "post_prod_to_feed_high_dev",
                                        "other_waste_to_feed_low_dev", "other_waste_to_feed_high_dev"])
    cols = waste_ratios.columns.to_list()
    ratio = lambda x: (x - cols[0])/(cols[-1] - cols[0])

    # if efficiency == "no_change":
    #     for item in waste_ratios.index.to_list():
    #         waste_ratios.loc[item] = [start_params[item] for x in cols]
    #
    # else:
    improvement = model_params.efficiency_improvement

    waste_ratios.loc["post_prod_high_dev"] = [start_params["post_prod_high_dev"]*(1 - improvement*ratio(x)) for x in cols]
    waste_ratios.loc["post_prod_low_dev"] = [start_params["post_prod_low_dev"] for x in cols]
    waste_ratios.loc["processing_high_dev"] = [start_params["processing_high_dev"]*(1 - improvement*ratio(x)) for x in cols]
    waste_ratios.loc["processing_low_dev"] = [start_params["processing_low_dev"]*(1 - improvement*ratio(x)) for x in cols]
    waste_ratios.loc["distribution_high_dev"] = [start_params["distribution_high_dev"]*(1 - improvement*ratio(x)) for x in cols]
    waste_ratios.loc["distribution_low_dev"] = [start_params["distribution_low_dev"]*(1 - improvement*ratio(x)) for x in cols]

    waste_ratios.loc["post_prod_to_feed_high_dev"] = [start_params["post_prod_to_feed_high_dev"]*(1 + improvement*ratio(x)) for x in cols]
    waste_ratios.loc["post_prod_to_feed_low_dev"] = [start_params["post_prod_to_feed_low_dev"]*(1 + improvement*ratio(x)) for x in cols]

    waste_ratios.loc["other_waste_to_feed_high_dev"] = [start_params["other_waste_to_feed_high_dev"]*(1 + improvement*ratio(x)) for x in cols]
    waste_ratios.loc["other_waste_to_feed_low_dev"] = [start_params["other_waste_to_feed_low_dev"]*(1 + improvement*ratio(x)) for x in cols]

    io.save("lib\\dat\\waste_vars", "food_waste_gen", waste_ratios)
