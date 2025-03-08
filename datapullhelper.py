import pybaseball as pyb
import pandas as pd
import threading as th
import os
from time import sleep
from timeit import default_timer

"""
Season Dates:

2021: Apr 1 - Nov 2 
2022: Apr 7 - Nov 5
2023: Mar 30 - Nov 1
2024: Mar 20 - Oct 30

All-encompassing dates:

Feb 14 - Dec 25 (these are arbitrary)
"""

#data importing utils

def get_all_files_in_directory(dir_path: str) -> [str]:
    file_list = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            file_list.append(dir_path + "/" + item)
    return file_list

def get_all_files() -> {str : [str]}:
    data = {}
    for yr in os.listdir("data/pitcher_data"):
        yr_path = "data/pitcher_data/" + yr
        data.update({yr : get_all_files_in_directory(yr_path)})
    return data

# data api grab utils

def cull_data(df: pd.DataFrame, cull_vars: [str]) -> pd.DataFrame:
    if cull_vars == []:
        return df
    else:
        return df[cull_vars]

def get_lookup(year: int, to_file: bool = True) -> pd.DataFrame:
    if to_file:
        ids = pyb.pitching_stats(year, end_season=None, league="all", qual=1, ind=0)[["IDfg"]]
        info = pyb.playerid_reverse_lookup(ids["IDfg"].values, "fangraphs").sort_values(by="name_last")
        info.to_excel(f"data/pitcher_data/{str(year)}/{str(year)}_pitcher_metadata.xlsx")
        print("wrote metadata file")
        return info[["key_mlbam", "name_last", "name_first"]]
    else:
        info = pd.read_excel(f"data/pitcher_data/{str(year)}/{str(year)}_pitcher_metadata.xlsx")
        return info[["key_mlbam", "name_last", "name_first"]]

def get_all_data(season_list: [[str, str]], to_file: bool, cull_vars: [str] = []) -> None:
    for season in season_list:
        th.Thread(target=get_season_data, args=(season, to_file, cull_vars)).start() # split workers to each year

def get_season_data(season: [str, str], to_file: bool, cull_vars: [str] = []) -> None:
    # get look up table for names/ids
    year = int(season[0][:4])
    pitcher_info = get_lookup(year, True) # SWITCH TO TRUE IF YOU WANT TO REGEN DATA
    pitcher_ids = pitcher_info["key_mlbam"]
    pitcher_name= pitcher_info["name_last"] + "_" + pitcher_info["name_first"]
    lookup = {pitcher_ids[i] : pitcher_name[i] for i in range(len(pitcher_ids))}
    for id in pitcher_ids.head():
        th.Thread(target=get_pitcher_data, args=(season, id, lookup, True, cull_vars)).start() #split off into per query workers
        sleep(0.5) #to prevent rate limit

def get_pitcher_data(season: [str, str], id: int, lookup: dict, to_file: bool = True, cull_vars: [str] = []):
    data = cull_data(pyb.statcast_pitcher(season[0], season[1], id), cull_vars)
    path = f"data/pitcher_data/{season[0][:4]}/{lookup[id]}.xlsx"
    if to_file:
        data.to_excel(path)
        print(f"wrote {path}")

"""
# get the preliminary metadata loaded into variables:

pitcher_info = pd.read_excel("data/pitcherinfo.xlsx")

pitcher_ids = pitcher_info["key_mlbam"]
pitcher_name= pitcher_info["name_last"] + "_" + pitcher_info["name_first"]

# lookup table that converts MLBAM id's to last_first name
lookup = {pitcher_ids[i] : pitcher_name[i] for i in range(len(pitcher_ids))}
"""