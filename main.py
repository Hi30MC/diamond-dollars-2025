import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels as sm
import datapullhelper as dp
import datacalchelper as dc
import dataparse as parse

# init pitcher list, only need to do once, so commented for now to save runtime
# dp.get_pitcher_info()

# list of seasons to pull data for
season_list = [[j + "-02-14", j+ "-12-25"] for j in [str(i) for i in range(2021, 2025)]]
# list of variables to keep (cull_vars)
cull_vars = "game_date events description zone des type hit_location bb_type balls strikes on_3b on_2b on_1b outs_when_up inning inning_topbot at_bat_number pitch_number home_score away_score".split(" ")

# RUN ONLY WHEN NEED TO REGEN DATA
# dp.get_all_data(season_list=season_list, to_file=True, cull_vars=cull_vars)

parse.write_relief_files("2021 2022 2023 2024".split())
# parse.write_save_files("2021 2022 2023 2024".split())



# s1 = pd.DataFrame({"CAR":[1,2], "ABS":[3,4], "BUM":[5,6]}).set_axis(["x", "y"]).T

# print(s1.sort_index().reset_index(names="name"))

# s2 = pd.Series([1, 2]).set_axis(["x", "y"])._set_name("A")
# s3 = pd.Series([3, 4]).set_axis(["x", "y"])._set_name("B")

