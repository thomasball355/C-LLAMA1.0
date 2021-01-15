import pickle
import pandas as pd
import numpy as np
import os


def dirs(directory, *args):
    string = f"{directory}\\"
    for arg in args:
        string += f"\\{arg}"
    if os.path.isdir(string) == False:
        os.makedirs(string)
        print(f"Made dir \"{string}\"")


def save(path, data_name, data):
    dirs(f"{path}")
    with open(f"{path}\\{data_name}.obj", "wb") as f:
        pickle.dump(data, f)
    print(f"Pickled \"{data_name}\" to \"{path}\"")
    return


def load(path, data_name):
    with open(f"{path}\\{data_name}.obj", "rb") as f:
        data = pickle.load(f)
    return data


def format_upper(input):
    char_list = "QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnmÔ"
    def form(input):
        for char in input:
            if char not in char_list:
                input = input.replace(char, "")
        input = input.upper()
        return input
    if type(input) is str:
        input = form(input)
    elif type(input) is list:
        input = [form(x) for x in input]
    return input


def re_index_area(df):
    idx = df.index
    replace_dict = {}
    for item in idx.levels[0]:
        replace_dict[item] = format_upper(item)
    idx = idx.set_levels(idx.levels[0].map(replace_dict.get), level = "Area")
    df.index = idx
    return df

def re_index_area2(df):
    idx = df.index
    replace_dict = {}
    for item in idx.levels[0]:
        replace_dict[item] = format_upper(item)
    idx = idx.set_levels(idx.levels[0].map(replace_dict.get), level = "Country Name")
    df.index = idx
    return df
