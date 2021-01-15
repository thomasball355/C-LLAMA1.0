"""
C-LLAMA - Ball, T. 2021.

C-LLAMA.py is the core module of the model, from which all other modules
are run. Run this file (ie - 'python C-LLAMA.py' to run the model). The
model must be run in it's entirety once. Afterward the "stage_" functions
down below can be commented out if changes have only been made to later stages.
At some point in the future I will change this so stages of the model can be run
from the command line (or even better from a GUI).

All instances of a 'dev_metric' are referred to in any surrounding literature as
'industrialisation_metric', as this is a truer reflection of the metric.

In theory, 'initialise.py' should check for installed packages and install any
that are missing, but currently this functionality doesn't always work properly so
required packages might need to be installed manually. Fortunately they're all
common Python libraries.
"""

try:
    import pandas as pd
    import numpy as np
    import pickle
    import matplotlib.pyplot as plt

    import initialise
    import model_params

    # stage 1
    import lib.mod.dev_metric
    import lib.mod.food_waste_gen
    import lib.mod.dev_metric_calculations
    import lib.mod.diet_makeup
    import lib.mod.crop_yield_and_production_hist
    import lib.mod.crop_yield_and_production_params
    import lib.mod.crop_yield_projection
    import lib.mod.food_demand_and_waste_production
    # stage 2
    import lib.mod.crop_production_ratios
    import lib.mod.crop_and_livestock_production
    import lib.mod.livestock_feed_demand
    import lib.mod.harvest_residues
    # stage 3
    import lib.mod.fodder_crops
    # stage 4
    import lib.mod.pasture_land_calculations
    import lib.mod.crop_land_calculations
    # stage 5
    import lib.mod.land_use_calculations

    # functions etc
    import lib.funcs.dat_io as io
    import lib.dat.continents
    import lib.dat.food_commodity_seperation as fcs

    initialise.population_sort()
    area_index = initialise.generate_area_index()

    io.dirs(model_params.land_use_data_out_path)

    # main loop
    def stage_1():

        lib.mod.food_waste_gen.main() # no_change, medium, high

        # Loop over continents
        for continent in lib.dat.continents.continents:

            # Loop over subcontinent regions
            for region in lib.dat.continents.continents[continent]:

                continent = io.format_upper(continent)
                region = io.format_upper(region)
                path = f"data\\{continent}\\{region}"

                FBS_data = io.load(path, f"FoodBalanceSheets_E_{region}").copy()
                PC_data = io.load(path, f"Production_Crops_E_{region}").copy()

                # Loop over countries
                for area in area_index[area_index.Region == region].index.to_list():

                    lib.mod.dev_metric.main(FBS_data.xs(area, level = "Area"),
                                            continent, region, area, path)

                    lib.mod.dev_metric_calculations.main(continent, region, area,
                                                        path)

                    lib.mod.diet_makeup.main(FBS_data.xs(area, level = "Area"),
                                                continent, region, area, path)

                    lib.mod.crop_yield_and_production_hist.main(PC_data, continent,
                                                                region, area, path)

                # calculate per-crop max yield for each region
                lib.mod.crop_yield_and_production_params.main(  [io.load(path, "_yield_max_vals_temp"),
                                                                io.load(path, "_yield_min_vals_temp"),
                                                                io.load(path, "_prod_ratios_temp")],
                                                                continent, region, path)

                # Loop over countries
                for area in area_index[area_index.Region == region].index.to_list():

                    lib.mod.crop_yield_projection.main(continent, region, area, path)

                    lib.mod.food_demand_and_waste_production.main(continent, region, area, path)


    def stage_2():

        #Crop production for human consumption (global pool)

        lib.mod.crop_production_ratios.main(area_index)

        lib.mod.crop_and_livestock_production.main(area_index)

        for continent in lib.dat.continents.continents:

            for region in area_index[area_index.Continent == continent].Region.to_list():

                for area in area_index[area_index.Region == region].index.to_list():

                    path = f"data\\{continent}\\{region}"

                    lib.mod.livestock_feed_demand.main(continent, region, area, path)

                    lib.mod.harvest_residues.main(continent, region, area, path)


    def stage_3():

        # use HR for feed then output fodder energy demand
        lib.mod.fodder_crops.main(area_index)

    def stage_4():

        lib.mod.pasture_land_calculations.main(area_index)

        lib.mod.crop_land_calculations.main(area_index)

    def stage_5():

        lib.mod.land_use_calculations.main(area_index)

    stage_1()
    stage_2()
    stage_3()
    stage_4()
    stage_5()

except KeyboardInterrupt:
    print("Stopping!")
    quit()
