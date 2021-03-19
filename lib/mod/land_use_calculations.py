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

import model_params

def main(area_index):

    land_use_dat = pd.read_csv("data\\Inputs_LandUse_E_All_Data_NOFLAG.csv",
                                encoding = "latin-1",
                                index_col = ["Area", 'Item Code',
                                'Item', 'Element Code', 'Element', 'Unit'])
    land_use_dat = io.re_index_area(land_use_dat)

    crop_list = lib.dat.food_commodity_seperation.big_list
    fodder_list = lib.dat.fodder_crops.fodder_crops

    fodder_list_red = [x for x in fodder_list if x not in crop_list] + ["Other feed"]

    global_land_use_proj = pd.DataFrame(
                                index = ["Fodder Crops", "Food Crops", "Pasture"],
                                columns = np.arange(2013, 2051, 1), data = 0)
    global_land_use_proj_adjusted = pd.DataFrame(
                                index = ["Pasture", "Fodder Crops", "Food Crops"],
                                columns = np.arange(2013, 2051, 1), data = 0)
    global_land_use_proj_adjusted_disagg = pd.DataFrame(
                                index = crop_list + fodder_list_red + ["Pasture"],
                                columns = np.arange(2013, 2051, 1), data = 0)

    global_land_use_hist = pd.DataFrame(
                                index = ["Cropland", "Pasture"],
                                columns = np.arange(1961, 2019, 1), data = 0)

    global_output_dat = pd.DataFrame()
    global_output_dat_grouped = pd.DataFrame()
    cont_labels = []
    region_labels = []
    area_labels = []
    item_labels = []
    unit_labels = []
    cont_labels_g = []
    region_labels_g = []
    area_labels_g = []
    item_labels_g = []
    unit_labels_g = []
    crop_not = []
    past_not =[]
    for continent in area_index.Continent.unique():

        for region in area_index[area_index.Continent == continent].Region.unique():

            path = f"data\\{continent}\\{region}"

            for area in area_index[area_index.Region == region].index.to_list():

                area_land_use_proj = pd.DataFrame(
                                index = ["Food Crops", "Pasture", "Fodder Crops"],
                                columns = np.arange(2013, 2051, 1))
                area_land_use_proj_adjusted = pd.DataFrame(
                                index = ["Food Crops", "Pasture", "Fodder Crops"],
                                columns = np.arange(2013, 2051, 1))
                area_land_use_proj_adjusted_disagg = pd.DataFrame(
                                index = crop_list + fodder_list_red + ["Pasture"],
                                columns = np.arange(2013, 2051, 1))

                land_use_dat_area = land_use_dat.xs(area,
                                                    level = "Area").fillna(
                                                    method = "backfill",
                                                    axis = 1).fillna(0)

                crop_land_projection = io.load(path,
                                        f"land_use\\crop_area_{area}").fillna(0)
                pasture_land_projection = io.load(path,
                                    f"land_use\\pasture_area_{area}").fillna(0)
                fodder_land_projection = io.load(path,
                                    f"land_use\\fodder_area_{area}").fillna(0)

                area_land_use_proj.loc["Pasture"] = pasture_land_projection
                global_land_use_proj.loc["Pasture"] += pasture_land_projection
                area_land_use_proj.loc["Fodder Crops"] = np.sum(fodder_land_projection,
                                                                        axis = 0)
                global_land_use_proj.loc["Fodder Crops"] += np.sum(fodder_land_projection,
                                                                axis = 0).values
                area_land_use_proj.loc["Food Crops"] = np.sum(crop_land_projection,
                                                                axis = 0).values
                global_land_use_proj.loc["Food Crops"] += np.sum(crop_land_projection,
                                                                axis = 0).values

                adjust = True   # not perfect - difficult to inform ratio of
                                # fodder to non-fodder in a meaningful way
                if adjust == True:
                    crop_hist = land_use_dat_area.xs("Cropland", level = "Item") * 1000
                    crop_recent_val = crop_hist.values[0][-1]
                    try:
                        food_ratio = area_land_use_proj[2017].loc["Food Crops"] /\
                                    (area_land_use_proj[2017].loc["Food Crops"] +\
                                    area_land_use_proj[2017].loc["Fodder Crops"]) * 1.3
                    except ZeroDivisionError:
                        food_ratio = 0.7
                    fodder_ratio = 1 - food_ratio
                    delta = crop_recent_val - (area_land_use_proj.loc["Food Crops"][2017]\
                                            + area_land_use_proj.loc["Fodder Crops"][2017])
                    food_delta = delta * food_ratio
                    fodder_delta = delta * fodder_ratio
                else:
                    food_delta = 0
                    fodder_delta = 0

                area_land_use_proj_adjusted.loc["Fodder Crops"] = np.sum(fodder_land_projection,
                                                                        axis = 0).values + fodder_delta
                global_land_use_proj_adjusted.loc["Fodder Crops"] += np.sum(fodder_land_projection,
                                                                axis = 0).values + fodder_delta
                area_land_use_proj_adjusted.loc["Food Crops"] = np.sum(crop_land_projection,
                                                                axis = 0).values + food_delta
                global_land_use_proj_adjusted.loc["Food Crops"] += np.sum(crop_land_projection,
                                                                axis = 0).values + food_delta

                for crop in crop_land_projection.index.to_list():

                    if np.nansum(crop_land_projection[2017]) != 0:
                        ratio = crop_land_projection[2017].loc[crop] / np.nansum(crop_land_projection[2017])
                    else:
                        ratio = 0

                    global_land_use_proj_adjusted_disagg.loc[crop] += (crop_land_projection.loc[crop] + (food_delta * ratio)).values
                    area_land_use_proj_adjusted_disagg.loc[crop] = (crop_land_projection.loc[crop] + (food_delta * ratio)).values

                for crop in fodder_land_projection.index.to_list():

                    if np.nansum(fodder_land_projection[2017]) != 0:
                        ratio = fodder_land_projection[2017].loc[crop] / np.nansum(fodder_land_projection[2017])
                    else:
                        ratio = 0

                    crop_conv = {
                                "Other feed" : "Other",
                                "Barley and products" : "Cereals - Excluding Beer",
                                "Sorghum and products" : "Cereals - Excluding Beer",
                                "Sugar beet" : "Sugar & Sweeteners"
                                }

                    if crop in crop_conv.keys():
                        crop_x = crop_conv[crop]
                    else:
                        crop_x = crop

                    global_land_use_proj_adjusted_disagg.loc[crop_x] = np.nansum([
                                global_land_use_proj_adjusted_disagg.loc[crop_x],
                                (fodder_land_projection.loc[crop] + (fodder_delta * ratio)).values],
                                axis = 0)

                    area_land_use_proj_adjusted_disagg.loc[crop_x] = np.nansum([
                                    area_land_use_proj_adjusted_disagg.loc[crop_x],
                                    (fodder_land_projection.loc[crop] + (fodder_delta * ratio)).values],
                                    axis = 0)

                try:
                    global_land_use_hist.loc["Cropland"] += land_use_dat_area.xs(
                                        "Cropland", level = "Item").values[0]
                except KeyError:
                    pass
                    crop_not.append(area)
                try:
                    pasture_hist = land_use_dat_area.xs(
                        "Land under perm. meadows and pastures", level = "Item")
                    global_land_use_hist.loc["Pasture"] += pasture_hist.values[0]
                except KeyError:
                    pasture_hist = land_use_dat_area.xs(
                                            "Country area", level = "Item") * 0
                    past_not.append(area)

                area_land_use_proj_adjusted.loc["Pasture"] = pasture_land_projection
                area_land_use_proj_adjusted_disagg.loc["Pasture"] = pasture_land_projection

                global_land_use_proj_adjusted.loc["Pasture"] += pasture_land_projection
                global_land_use_proj_adjusted_disagg.loc["Pasture"] += pasture_land_projection

                area_land_use_proj_adjusted_disagg = area_land_use_proj_adjusted_disagg\
                            [(area_land_use_proj_adjusted_disagg.T != 0).all()]
                area_land_use_proj_adjusted_disagg = area_land_use_proj_adjusted_disagg.dropna()

                ix = area_land_use_proj_adjusted_disagg.index.to_list()
                cont_labels = cont_labels + [continent for x in ix]
                region_labels = region_labels + [region for x in ix]
                area_labels = area_labels + [area for x in ix]
                item_labels = item_labels + [x for x in ix]
                unit_labels = unit_labels + ["ha" for x in ix]

                ix_g = area_land_use_proj_adjusted.index.to_list()
                cont_labels_g = cont_labels_g + [continent for x in ix_g]
                region_labels_g = region_labels_g + [region for x in ix_g]
                area_labels_g = area_labels_g + [area for x in ix_g]
                item_labels_g = item_labels_g + [x for x in ix_g]
                unit_labels_g = unit_labels_g + ["ha" for x in ix_g]

                global_output_dat = pd.concat([global_output_dat,
                                            area_land_use_proj_adjusted_disagg],
                                            axis = 0)
                global_output_dat_grouped = pd.concat([global_output_dat_grouped,
                                            area_land_use_proj_adjusted],
                                            axis = 0)



    def plot_global():
        global_land_use_proj_adjusted_disagg.T.plot.area()
        plt.show()

        plt.stackplot(np.arange(2013, 2051, 1),
                        global_land_use_proj_adjusted.values,
                        alpha = 0.85,
                        colors = ["#DF3033", "#309FDF", "#8FDF30"],
                        labels =    ["Pasture",
                                    "Fodder crops",
                                    "Crops for human consumption"]
                                    )
        plt.legend()
        plt.show()


    index_labels = [cont_labels,
                    region_labels,
                    area_labels,
                    item_labels,
                    unit_labels]

    idx = pd.MultiIndex.from_arrays(
                                        index_labels,
                                        names = ["Continent", "Region", "Area",
                                                "Item", "Unit"])

    global_output_dat.index = idx

    out_path = model_params.land_use_data_out_path
    out_name = model_params.land_use_data_out_name
    #out_name = io.load(".", "sfwflabel")

    global_output_dat.to_csv(f"{out_path}\\land_use_{out_name}.csv")

    index_labels = [cont_labels_g,
                    region_labels_g,
                    area_labels_g,
                    item_labels_g,
                    unit_labels_g]

    idx = pd.MultiIndex.from_arrays(
                                        index_labels,
                                        names = ["Continent", "Region", "Area",
                                                "Item", "Unit"])

    global_output_dat_grouped.index = idx

    global_output_dat_grouped.to_csv(f"{out_path}\\land_use_grouped_{out_name}.csv")

    # l1 = land_use_dat.index.get_level_values("Area").unique().to_list()
    # l2 = area_index.index.to_list()
    #
    # print(l3)
