import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels as sm
import datapullhelper as dp
import datacalchelper as dc

# init pitcher list, only need to do once, so commented for now to save runtime
# dp.get_pitcher_info()

# get the preliminary metadata loaded into variables:

pitcher_info = pd.read_excel("data/pitcherinfo.xlsx")

pitcher_ids = pitcher_info["key_mlbam"]
pitcher_name= pitcher_info["name_last"] + "_" + pitcher_info["name_first"]

# lookup table that converts MLBAM id's to last_first name
lookup = {pitcher_ids[i] : pitcher_name[i] for i in range(len(pitcher_ids))}

# list of seasons to pull data for
season_list = [[j + "-02-14", j+ "-12-25"] for j in [str(i) for i in range(2021, 2025)]]
# list of variables to keep (cull_vars)
cull_vars = "game_date events description zone des type hit_location bb_type balls strikes on_3b on_2b on_1b outs_when_up inning inning_topbot at_bat_number pitch_number home_score away_score".split(" ")

# example of how to get data for a single pitcher
# data = dp.get_data(lookup, [["2021-02-14", "2021-12-25"]], 521230, False, c-ull_vars)

# example of how to get data for all pitchers in a season
# data = dp.get_all_data(lookup, season_list, pitcher_ids, True, cull_vars)

# example of how to get sheet from dir to var
# data = pd.read_excel("data/pitcher_data/2021/akin_keegan.xlsx", sheet_name="Sheet1")

# get all files in 2021 directory
# dp.get_all_files_in_directory("data/pitcher_data/2021")

# get all data file names
# dp.get_all_files()