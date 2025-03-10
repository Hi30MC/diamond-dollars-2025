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
# run_fxn_wait([parse.write_relief_files], (years,))
# run_fxn_wait([parse.write_save_files], (years,))


# model data

# get global means

# print(parse.gen_relief_mean_data(years))
# print(parse.gen_save_mean_data(years))

# get seasonal stds

# print(parse.gen_global_stds_file(years))

# get p-value sheets (global stats only)

# for year in years:
#     players = [*pd.read_excel(f"data/calcs/save_calcs/{year}_mean_data.xlsx", index_col=0).index][:-1]
#     for player in players:
#         svm.get_s_values(player, year)
    

#get conglomerated s-values

# out = svm.get_s_values_conglomerated(years[0]).rename(years[0]).to_frame()
# print(out)
# for year in years[1:]:
#     out = pd.concat([out, svm.get_s_values_conglomerated(year).rename(year).to_frame()], axis=1) 
#     print(out)
# out.to_excel("data/s_vals/conglomerated_s_val_data.xlsx")
# apply model

data = pd.read_excel("data/s_vals/conglomerated_s_val_data.xlsx", index_col=0)

out = {}
for col in data.columns:
    datacol = data[col].dropna()
    meadian = datacol.median()
    q3, q1 = np.percentile(datacol, [75 ,25])
    q3, q1 = q3*1.5, q1*1.5
    iqr = q3 - q1
    max = meadian + iqr
    tot = 0
    ct = 0
    for val in datacol:
        if val < max:
            ct += 1
            tot += val
    out.update({col: [tot/ct, max]})
means = pd.DataFrame(out).T.rename(columns={0: "mean excl outliers",1: "mean + 1.5iqr"})  
print(means)

out = {}
for col in data.columns:
    datacol = data[col].dropna()
    mean, max = means.T[col].values
    
    ct = 0
    resids = 0
    for val in datacol:
        if val < max:
            ct += 1
            resids += (val - mean)**2
    out.update({col: resids/ct})
resids = pd.Series(out).rename("stds")
stats = means.join(resids)
print(stats)