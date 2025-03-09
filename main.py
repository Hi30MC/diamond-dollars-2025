import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels as sm
import datapullhelper as dp
import datacalchelper as dc
import dataparse as parse

import reliefmodel as rlm
import savemodel as svm


#meta-meta data 
years = "2021 2022 2023 2024".split()
season_list = [[f"{y}-02-14", f"{y}-12-25"] for y in years]
cull_vars = "game_date events description zone des type hit_location bb_type balls strikes on_3b on_2b on_1b outs_when_up inning inning_topbot at_bat_number pitch_number home_score away_score".split(" ")

#regen metadata
# for year in years:
#     dp.get_metadata(year)

# regen all raw data
# dp.get_all_data(season_list, cull_vars, True)

# grab missing/not force regen
# dp.get_all_data(season_list, cull_vars, False)

# parse data, only run when needed
# parse.write_relief_files(years)
parse.write_save_files(years)

# model data

# apply model

