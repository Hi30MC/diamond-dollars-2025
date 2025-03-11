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


# get missing if needed
# print(dp.get_missing())


# regen all raw data
# run_fxn_wait([dp.get_all_data], (season_list, cull_vars, True))


# grab missing/not force regen
# run_fxn_wait([dp.get_all_data], (season_list, cull_vars, False))


# parse data, only run when needed, wait until done to model etc
run_fxn_wait([parse.write_relief_files], (years,))
# run_fxn_wait([parse.write_save_files], (years,))


# Save Model

# get global means, get seasonal stds, create combined mu and sigma lookup tables

# for year in years:
#     svm.get_save_data_year_file(year)

# svm.get_save_data_global(years)

# get all s-value sheets (global stats only)    

# svm.write_s_vals(years)

# get mu, std for s_values

# svm.get_s_val_meta(years)

# apply cutoff to s_val sheets (files must exist)

# svm.update_s_val_sheets(years)

# make global s count sheet w/ totals and %ages

# svm.get_s_val_master_sheet(years)

# Relief Model

# get mu std

# rlm.write_mu_std(years)

# get r-score

# rlm.write_r_scores(years)

# print(parse.convert_to_relief("/home/ad/Documents/code/diamond-dollars-2025/data/pitcher_data/2021/finnegan_kyle.xlsx", 0, "2021"))