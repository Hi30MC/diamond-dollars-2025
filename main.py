import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels as sm
import datapullhelper as dp
import datacalchelper as dc

# init pitcher list, only need to do once, so commented for now to save runtime
# dp.get_pitcher_info()

# list of seasons to pull data for
season_list = [[j + "-02-14", j+ "-12-25"] for j in [str(i) for i in range(2021, 2025)]]
# list of variables to keep (cull_vars)
cull_vars = "game_date events description zone des type hit_location bb_type balls strikes on_3b on_2b on_1b outs_when_up inning inning_topbot at_bat_number pitch_number home_score away_score".split(" ")

# RUN ONLY WHEN NEED TO REGEN DATA
dp.get_all_data(season_list=season_list, to_file=True, cull_vars=cull_vars)