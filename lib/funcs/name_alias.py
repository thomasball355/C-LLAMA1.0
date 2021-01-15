import lib.dat.food_commodity_seperation

lookup = lib.dat.food_commodity_seperation.name_conv

def conv(string):
    def get_key(val):
        for key, value in lookup.items():
             if val == value:
                 return key
    if string in lookup.keys():
        return lookup[string]
    else:
        return string
