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
# from ftfy import fix_encoding()

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

# used to get era data tables manually


# data = pyb.pitching_stats_bref(year)[["Name", "ERA"]]#.set_index("Name")

# Parse to folders

# parse data, only run when needed, wait until done to model etc
run_fxn_wait([parse.write_relief_files], (years,))
# run_fxn_wait([parse.write_save_files], (years,))

#testing
# parse.write_relief_files_in_year("2021")

# print(parse.convert_to_relief("data/pitcher_data/2021/akin_keegan.xlsx", 0, "2021"))

# pyb.pitching_stats_bref(2021).to_excel("2021_season_data.xlsx")


"""
# clean relief data

# for year in years:
#     data = pd.read_excel(f"data/relief_data/{year}.xlsx", index_col=0)
#     out = data.loc[0].to_frame()
#     for i, row in [*data.iterrows()][1:]: 
#         # print(i,row)
#         if not row.empty:
#             out = out.join(row.to_frame())
#     out.T.to_excel(f"data/relief_data/{year}_clean.xlsx")
"""

# Save Model (works fine)

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

# def get_era_data(year):
#     # year = 2021
#     data = pd.read_excel(f"data/pitcher_data/{year}_era_data.xlsx")
#     data.to_csv(f"{year} test.csv")

#     data = pd.read_csv(f"{year} test.csv", encoding="utf-8", index_col=0)
#     # print(data[["Name", "ERA"]])
#     data = data[["Name", "ERA"]]
#     data["Name"] = [s.lower() for s in data["Name"]]
#     print(data.head())
#     data.to_excel(f"{year}_era_data.xlsx")

#     data.to_excel(f"data/pitcher_data/{year}_era_data.xlsx")



# def get_missing(year):
#     get_era_data(year)
#     paths = dp.get_all_files_in_directory(f"data/pitcher_data/{year}")
#     names = [dp.path_to_name(path) for path in paths]
#     converted = []
#     for name in names[1:]:
#         last, first = name.split("_")
#         if "." in [*first]:
#             a, b  = first.split()
#             first = a+b
#         converted.append(f"{first} {last}")
#     converted = sorted(converted)
#     avail = pd.read_excel(f"{year}_era_data.xlsx", index_col=0)["Name"].sort_values()
#     out = pd.Series([name if name not in avail.values else -1 for name in converted])
#     return out.loc[out.values != -1].reset_index(drop=True)

# def get_missing_era(years):
#     out = pd.concat([get_missing(year).rename(year) for year in years], axis=1)
#     print(out)
#     return out

# get_missing_era(years).to_excel("missing_era.xlsx")


# Relief Model (works minus era)

# print(dc.get_era_season(name, dc.get_era_lookup(2021)))

# get mu std

rlm.write_mu_std(years)

# get r-score

rlm.write_r_scores(years)

print("Done!")
