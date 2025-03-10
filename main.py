import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels as sm
import datapullhelper as dp
import datacalchelper as dc
import dataparse as parse
import threading as th

import reliefmodel as rlm
import savemodel as svm


#meta-meta data 
years = "2021 2022 2023 2024".split()
season_list = [[f"{y}-02-14", f"{y}-12-25"] for y in years]
cull_vars = "game_date events description zone des type hit_location bb_type balls strikes on_3b on_2b on_1b outs_when_up inning inning_topbot at_bat_number pitch_number home_score away_score".split(" ")

def run_fxn_wait(func_list, args) -> None:
    threadlist = []
    helper = th.Thread(target= lambda out, func_list, args: out.extend([t for t in [func(*args,) for func in func_list]]), args=(threadlist, func_list, args))
    helper.start()
    helper.join()
    print(threadlist)
    for t in threadlist[0]:
        t.join()

#regen metadata
# for year in years:
#     dp.get_metadata(year)

# print(dp.get_missing())

# regen all raw data
# run_fxn_wait([dp.get_all_data], (season_list, cull_vars, True))

# grab missing/not force regen
# run_fxn_wait([dp.get_all_data], (season_list, cull_vars, False))

# dp.get_pitcher_data(season_list[2], 621237, dp.get_lookup("2023", False), cull_vars, True)

# parse data, only run when needed, wait until done to model etc
# run_fxn_wait([parse.write_relief_files], (years,))
# run_fxn_wait([parse.write_save_files], (years,))


# model data

# get global means

# print(parse.gen_relief_mean_data(years))
# print(parse.gen_save_mean_data(years))

# get seasonal stds

# print(parse.gen_global_stds_file(years))

# print(svm.get_s_values("finnegan_kyle", "2021"))

# get p-value sheets (global stats only)

for year in years[2:4]:
    players = [*pd.read_excel(f"data/calcs/save_calcs/{year}_mean_data.xlsx", index_col=0).index][:-1]
    for player in players:
        svm.get_s_values(player, year)
    
# apply model
