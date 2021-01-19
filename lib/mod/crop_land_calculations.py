import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import scipy.stats as stat

import lib.funcs.perc_contributions_WRAP
import lib.funcs.dat_io as io
import lib.funcs.foodsupply_trajectory
import lib.funcs.name_alias
import lib.dat.colours
import lib.dat.food_commodity_seperation
import lib.dat.fodder_crops


def main(area_index):

    def line(dat, dat_start, dat_end):
        years = np.arange(dat_start, dat_end + 1, 1)
        line_params = stat.linregress(years, dat)
        return line_params

    land_use_dat = pd.read_csv("data\\Inputs_LandUse_E_All_Data_NOFLAG.csv",
                                encoding = "latin-1",
                                index_col = ["Area", 'Item Code',
                                'Item', 'Element Code', 'Element', 'Unit'])
    land_use_dat = io.re_index_area(land_use_dat)

    fodder_crops_list = lib.dat.fodder_crops.fodder_crops
    fodder_crops_properties = pd.read_excel("lib\\dat\\fodder_product_properties.xlsx", index_col = 0)

    for continent in area_index.Continent.unique():

        for region in area_index[area_index.Continent == continent].Region.unique():

            path = f"data\\{continent}\\{region}"
            FBS_dat = io.load(path, f"FoodBalanceSheets_E_{region}")
            production_dat = io.load(path, f"Production_Crops_E_{region}")

            for area in area_index[area_index.Region == region].index.to_list():

                area_land_use = land_use_dat.xs(area, level = "Area")

                # load yield projections
                crop_yield_projection = io.load(path, f"yield_production\\yield_projection_{area}") # tonnes/ha/year

                # load crop production demand
                crop_production_demand = io.load(path, f"production\\production_mass_vegetal_for_human_{area}") #kg/year
                crop_production_demand = crop_production_demand / 1000 # tonnes/year

                crop_yield_projection = crop_yield_projection.replace(0, np.nan)
                crop_land_area_projection = crop_production_demand / crop_yield_projection.values # ha
                cropland_hist = area_land_use.xs("Arable land", level = "Item")

                # do yield projection for fodder
                fodder_production_quota = io.load(path, f"livestock\\fodder_production_quota_{area}") # MJ / year
                production_hist = production_dat.xs(area, level = "Area").xs("Production", level = "Element")
                yield_hist = production_dat.xs(area, level = "Area").xs("Yield", level = "Element") * 1E-04

                # create receiving dataframe
                fodder_yield = pd.DataFrame(index = np.arange(2013, 2051, 1), columns = fodder_crops_list).T

                for crop in fodder_crops_list:

                    if crop not in crop_yield_projection.index.to_list():

                        crop_conv = lib.funcs.name_alias.conv(crop)

                        try:
                            if crop_conv == "Sugar beet":

                                fodder_yield.loc["Sugar beet"] = crop_yield_projection.loc["Sugar Crops"]

                            else:

                                data = yield_hist.xs(crop_conv, level = "Item")

                                years = 30

                                line_params = stat.linregress(np.arange(2018 - years, 2018, 1),
                                                            data.values[0][-years:])

                                slope = line_params[0]
                                intercept = line_params[1]
                                r = line_params[2]
                                p = line_params[3]

                                lin = lambda x: (x * slope) + intercept
                                val_2050 = lin(2050)
                                val_start = data.iloc[:, -5:].mean(axis = 1).values[0]
                                val_min = data.min(axis = 1).values[0]

                                lin2 = lambda x: val_start + ((x - 2013) * ((val_2050 - val_start) / (2050 - 2013)))
                                if r**2 > 0.2 and p < 0.05 and slope > 0:
                                    output = [val_min if lin2(x) < val_min else lin2(x) for x in np.arange(2013, 2050 + 1, 1)]
                                else:
                                    output = data.loc[crop].astype(float).iloc[-10:-1].mean()

                                fodder_yield.loc[crop] = output
                        except KeyError:
                            print(f"KeyError in {__name__}; no yield data for {crop} for {area}, using fallback yield value")

                    else:
                        fodder_yield.loc[crop] = crop_yield_projection.loc[crop]
                    if fodder_yield.loc[crop].isnull().values.any() == True and fodder_production_quota.loc[crop].sum(axis = 0) > 0:
                        fodder_yield.loc[crop] = fodder_crops_properties.loc[crop]["fallback_yield"]

                fodder_production_quota = fodder_production_quota.fillna(0) # MJ / year
                fodder_production_quota_mass = pd.DataFrame(columns = fodder_production_quota.columns, index = fodder_production_quota.index)

                for crop in fodder_crops_list:

                    energy_density = fodder_crops_properties.loc[crop_conv]["energy_density"] # MJ / kg
                    energy_density = energy_density * 1000 # MJ / tonne
                    fodder_production_quota_mass.loc[crop] = fodder_production_quota.loc[crop] / energy_density # tonnes / year

                fodder_land_area_projection = fodder_production_quota_mass / fodder_yield # ha

                io.save(f"{path}\\land_use", f"fodder_area_{area}", fodder_land_area_projection)
                io.save(f"{path}\\land_use", f"crop_area_{area}", crop_land_area_projection)
