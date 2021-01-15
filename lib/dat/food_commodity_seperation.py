vegetal_prods_grouped_list =    [
                                "Cereals - Excluding Beer",
                                "Fruits - Excluding Wine",
                                "Oilcrops",
                                "Pulses",
                                "Spices",
                                "Starchy Roots",
                                "Vegetable Oils",
                                "Vegetables",
                                "Sugar & Sweeteners"
                                ]

# These are taken as individual commodities
staple_crops =  [
                "Wheat and products",
                "Rice (Milled Equivalent)",
                "Maize and products",
                "Palm Oil",
                "Rape and Mustardseed",
                "Soyabeans",
                "Sunflower seed",
                "Potatoes and products",
                "Cassava and products",
                "Nuts and products"
                ]

# grouped as luxuries
luxuries =  [
            'Coffee and products',
            'Cocoa Beans and products',
            'Tea (including mate)',
            ]

alcohol =   [
            'Wine',
            'Beer',
            'Beverages, Fermented',
            'Beverages, Alcoholic',
            'Alcohol, Non-Food'
            ]

# animal products taken as individual commodities
animal_prods_list =     [
                        "Bovine Meat",
                        "Poultry Meat",
                        "Pigmeat",
                        "Mutton & Goat Meat",
                        "Meat, Other",
                        "Eggs"
                        ]

# grouped as dairy
dairy = [
        "Milk - Excluding Butter",
        "Butter, Ghee",
        "Cream"
        ]

# naming lookup
name_conv =     {
                "Wheat and products"        : "Wheat",
                "Rice (Milled Equivalent)"  : "Rice, paddy",
                "Maize and products"        : "Maize",
                "Palm Oil"                  : "Oil palm fruit",
                "Soyabeans"                 : "Soybeans",
                "Potatoes and products"     : "Potatoes",
                "Cassava and products"      : "Cassava",
                "Nuts and products"         : "Treenuts,Total",
                "Sorghum and products"      : "Sorghum",
                "Barley and products"       : "Barley"
                }

# big list
big_list    = staple_crops + vegetal_prods_grouped_list\
            + ["Luxuries (excluding Alcohol)", "Alcohol"]\
            + ["Other"]
