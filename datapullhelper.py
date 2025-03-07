import pybaseball as pyb
import pandas as pd

"""
Season Dates:

2021: Apr 1 - Nov 2 
2022: Apr 7 - Nov 5
2023: Mar 30 - Nov 1
2024: Mar 20 - Oct 30

All-encompassing dates:

Feb 14 - Dec 25 (these are arbitrary)
"""

def get_pitcher_info():
    data = pyb.pitching_stats(2022, end_season=None, league='all', qual=1, ind=0)[["IDfg"]]
    info = pyb.playerid_reverse_lookup(data["IDfg"].values, "fangraphs").sort_values(by="name_last")
    info.to_excel("data/pitcher_data/pitcherinfo.xlsx", index=False)

def cull_data(df: pd.DataFrame, cull_vars: [str]) -> pd.DataFrame:
    if cull_vars == []:
        return df
    else:
        return df[cull_vars]

def get_data(lookup: dict, season:str, id: int, toFile: bool = False, cull_vars: [str] = []) -> pd.DataFrame:
    data = cull_data(pyb.statcast_pitcher(season[0], season[1], id), cull_vars)
    path = "data/pitcher_data/" + season[0][:4] + "/"+lookup[id] + ".xlsx"
    if toFile:        
        data.to_excel(path)
    return data

def get_all_data(lookup: dict, season_list: [[str, str]], pitcher_ids: [int], toFile: bool = False, cull_vars: [str] = []) -> pd.DataFrame:
    for season in season_list:
        for id in pitcher_ids:
            get_data(lookup, season, id, toFile, cull_vars)