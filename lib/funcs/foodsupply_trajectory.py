import pandas as pd
import numpy as np

def calories_trajectory(start_year, end_year, start_cals, end_cals, end_cals_year, post_consumer_waste):

    cols = np.arange(start_year, end_year + 1, 1)
    trajectory = pd.DataFrame(columns = cols, index = ["Food supply (kcal/capita/day)"])
    for col in trajectory:
        trajectory[col] = start_cals + ((end_cals * (1 + post_consumer_waste[col])) - start_cals) / (end_cals_year - start_year) * (col - start_year)

    return trajectory
