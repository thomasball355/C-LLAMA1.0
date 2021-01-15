import pandas as pd
import numpy as np
import scipy.stats as stat
import matplotlib.pyplot as plt
import random



def historic_ratio(input):
    output = pd.DataFrame(index = input.index, columns = input.columns)
    sum = np.sum(input, axis = 0)
    discard = 0
    for col in input:
        if sum[col] == 0.0:
            input[col] = np.nan
            discard += 1
            #print(f"No data for year {col}; {input}.")
        output[col] = input[col] / sum[col]
    return output

def percentage_contributions_II(
                            input,
                            end_year,
                            data_start,
                            data_end
                            ):

    # normalise input
    sum = np.sum(input, axis = 0)
    discard = 0
    for col in input:
        if sum[col] == 0.0:
            input[col] = np.nan
            discard += 1
            #print(f"No data for year {col}; {input}.")
        input[col] = input[col] / sum [col]
    output = pd.DataFrame(index = input.index, columns = np.arange(data_end, end_year + 1, 1))
    for item in input.index:
        line = stat.linregress(np.arange(data_start + discard, data_end + 1, 1), input.xs(item).iloc[discard:].to_list())
        if line[2]**2 > 0.3 and line[3] < 0.05:
            output.loc[item] = (line[0] * np.arange(data_end, end_year + 1, 1)) + line[1]
        else:
            output.loc[item] = [np.mean(input.xs(item).iloc[discard:].to_list()[-10:]) for x in np.arange(data_end, end_year + 1, 1)]
    output[output < 0] = 0.0
    for col in output:
        if np.sum(output, axis = 0)[col] > 1.0:
            output[col] = output[col] / np.sum(output, axis = 0)[col]

    return output

def percentage_contributions(
                            input,
                            end_year,
                            data_start,
                            data_end
                            ):

    # normalise input
    sum = np.sum(input, axis = 0)
    discard = 0

    for col in input:
        if sum[col] == 0.0:
            input[col] = np.nan
            discard += 1
            #print(f"No data for year {col}; {input}.")
        input[col] = input[col] / sum [col]
    output = pd.DataFrame(index = input.index, columns = np.arange(data_end, end_year + 1, 1))
    for item in input.index:
        line = stat.linregress(np.arange(data_start + discard, data_end + 1, 1), input.xs(item).iloc[discard:].to_list())
        end_val = (line[0] * 2050) + line[1]
        start_val = input.xs(item).iloc[discard:].to_list()[-1]
        if end_val < 0.0:
            end_val = 0.0
        if line[2]**2 > 0.2 and line[3] < 0.1:
            output.loc[item] = [start_val + ((x - data_end) * ((end_val - start_val)/(2050 - 2013))) for x in np.arange(data_end, end_year + 1, 1)]
        else:
            output.loc[item] = [np.mean(input.xs(item).iloc[discard:].to_list()[-5:]) for x in np.arange(data_end, end_year + 1, 1)]

    for col in output:
        output[col] = output[col] / np.sum(output, axis = 0)[col]

    return output


def fodder_percentage_contributions(
                            input,
                            end_year,
                            data_start,
                            data_end
                            ):

    # normalise input
    sum = np.nansum(input, axis = 0)
    discard = 0
    i = 0
    while sum[i] == 0.0:
        input.iloc[:, i] = 0.0
        discard += 1
        if discard > data_end - data_start:
            break
        i += 1

    output = pd.DataFrame(index = input.index, columns = np.arange(data_end, end_year + 1, 1))
    for item in input.index:
        try:
            line = stat.linregress(np.arange(data_start + discard, data_end + 1, 1), input.xs(item).iloc[discard:].to_list())
            if line[2]**2 > 0.2 and line[3] < 0.1:
                output.loc[item] = (line[0] * np.arange(data_end, end_year + 1, 1)) + line[1]
            else:
                output.loc[item] = np.mean(input.xs(item).iloc[discard:].to_list()[-10:-1])
        except ValueError:
            output.loc[item] = np.arange(data_end, end_year + 1, 1) * 0.0
    output[output < 0] = 0.0
    for col in output:
        if np.sum(output, axis = 0)[col] > 1.0:
            output[col] = output[col] / np.sum(output, axis = 0)[col]

    return output
