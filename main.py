import pybaseball as pb
import numpy as np
import pandas as pd
import statsmodels as sm

data = pb.pitching_stats(2022, end_season=None, league='all', qual=1, ind=0)[["IDfg"]]

# data.to_csv("data/testing3.csv", index=False)

print(data.head())

test = pb.playerid_reverse_lookup(data["IDfg"].values, "fangraphs").sort_values(by="name_last")

test.to_csv("data/pitcher_data/pitcherinfo.csv", index=False)
test.to_excel("data/pitcher_data/pitcherinfo.xlsx", index=False)