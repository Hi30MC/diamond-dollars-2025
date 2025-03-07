import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels as sm
import datapull as dp

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

# example of how to get data for a single pitcher
# data = dp.get_data([["2021-02-14", "2021-12-25"]], 521230, False)

# example of how to get data for all pitchers in a season
# data = dp.get_all_data(season_list, pitcher_ids, True)