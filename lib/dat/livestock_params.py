animal_processing_losses = 0.05

################################################################################

animal_prods_list = [       "Bovine Meat",
                            "Poultry Meat",
                            "Pigmeat",
                            "Mutton & Goat Meat",
                            "Meat, Other",
                            "Eggs"
                            ]
# grouped as dairy
dairy =                     ["Milk - Excluding Butter",
                            "Butter, Ghee",
                            "Cream"
                            ]

################################################################################

conversion_efficiency =     {
                            "Bovine Meat"          :   0.029,
                            "Poultry Meat"          :   0.13,
                            "Pigmeat"               :   0.09,
                            "Mutton & Goat Meat"    :   0.067,
                            "Meat, Other"           :   0.079, ## mean of the other commodities
                            "Eggs"                  :   0.17,
                            "Dairy"                 :   0.17,
                            }

################################################################################

energy_density =            { #MJ/kg
                             "Bovine Meat"          : 8.31,
                             "Pigmeat"              : 8.31,
                             "Poultry Meat"         : 8.31,
                             "Mutton & Goat Meat"   : 8.31,
                             "Meat, Other"          : 8.31,
                             "Dairy" 	            : 2.33,
                             "Eggs"                 : 5.86,
                             "Fish" 	            : 2.75,
                             "Tallow" 	            : 37.00
                             }

################################################################################

fed_without_forage_developed =   {
                                    "Bovine Meat"       : 0.50,
                                    "Poultry Meat"      : 1.00,
                                    "Pigmeat"           : 0.95,
                                    "Mutton & Goat Meat": 0.50,
                                    "Meat, Other"       : 0.50,
                                    "Eggs"              : 1.00,
                                    "Dairy"             : 0.50
                                    }
fed_without_forage_developing =   {
                                    "Bovine Meat"       : 0.10,
                                    "Poultry Meat"      : 0.75,
                                    "Pigmeat"           : 0.75,
                                    "Mutton & Goat Meat": 0.05,
                                    "Meat, Other"       : 0.10,
                                    "Eggs"              : 0.75,
                                    "Dairy"             : 0.10
                                    }

################################################################################

byproduct_feed_potential = {                        # [agri, pp, processing]
                            "Dairy"	                : [0.25, 0.0, 0.05],
                            "Bovine Meat"	        : [0.25, 0.0, 0.05],
                            "Eggs"	                : [0.0, 0.0, 0.11],
                            "Poultry Meat"	        : [0.0, 0.0, 0.11],
                            "Pigmeat"               : [0.05, 0.45, 0.15],
                            "Mutton & Goat Meat"    : [0.20, 0.0, 0.11],
                            "Meat, Other"           : [0.20, 0.0, 0.05]
                            }

################################################################################

pasture_factor =    {"Bovine Meat"          : 1.0,
                    "Poultry Meat"          : 0.1,
                    "Pigmeat"               : 0.1,
                    "Mutton & Goat Meat"    : 1.0,
                    "Meat, Other"           : 1.0,
                    "Eggs"                  : 0.1,
                    "Dairy"                 : 1.0
                    }

# TLU / ha
grazing_intensity_rosegrant_2009 =   {              #2000   #2030  #2050
                                        "CWANA"   : [0.052, 0.077, 0.083], # Central-west Asia and North Africa
                                        "ESAP"    : [0.044, 0.067, 0.067], # East and South Asia and the Pacific
                                        "LAC"     : [0.188, 0.293, 0.318], # Latin America and the Caribbean
                                        "NAE"     : [0.052, 0.063, 0.060], # NA and Europe
                                        "SSA"     : [0.062, 0.090, 0.090], # Sub-saharan Africa
                                        "Globe"   : [0.064, 0.094, 0.098]  # Global
                                        }


fwf_FALAFEL = {
                "Dairy"	                :0.40,
                "Bovine Meat"	        :0.45,
                "Eggs"	                :0.80,
                "Poultry Meat"          :0.80,
                "Mutton & Goat Meat"    :0.45,
                "Pigmeat"	            :0.80,
                "Meat, Other"           :0.45
                }
