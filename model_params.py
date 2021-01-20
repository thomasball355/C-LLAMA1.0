"""model_params.py"""
# prescribe an overall efficiency improvement
efficiency_improvement = 0.20 # by 2050

# 'idealised' calorie consumption (inc post production losses)
desired_cals_target = 3200
# Year to project toward the desired calorie value
dev_target_year = 2100

# modify final value of animal_product contribution to diet
#   additive; 0.1 will result a 10% increase in
#   vegetable product contribution to diet. Equivalent to a 10% reduction in all
#   animal product (energy) consumption
veg_change              = 0.0
#   0.1 will result in a 10% DECREASE in non-dairy animal product (meat)
#   consumption. Replaces the calories with a mix of vegetal and dairy.
non_dairy_animal_change = 0.0

# Used
waste_start_params =     {
                    "post_prod_high_dev"      :   0.25,
                    "post_prod_low_dev"       :   0.07,
                    "processing_high_dev"     :   0.06,
                    "processing_low_dev"      :   0.10,
                    "distribution_high_dev"   :   0.05,
                    "distribution_low_dev"    :   0.50,
                    "post_prod_to_feed_low_dev"     : 0.40,
                    "post_prod_to_feed_high_dev"    : 0.05,
                    "other_waste_to_feed_low_dev"   : 0.15,
                    "other_waste_to_feed_high_dev"  : 0.40
                    }

land_use_data_out_path = "..\\land_use_out"
land_use_data_out_name = "15perc_10veg_10vg"
