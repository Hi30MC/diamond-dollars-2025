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
    return sorted(file_list)

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

def get_metadata(year: str) -> pd.DataFrame:
    ids = pyb.pitching_stats(year, end_season=None, league="all", qual=1, ind=0)[["IDfg"]]
    info = pyb.playerid_reverse_lookup(ids["IDfg"].values, "fangraphs").sort_values(by="name_last")
    info.to_excel(f"data/pitcher_data/{str(year)}/{str(year)}_pitcher_metadata.xlsx")
    print("wrote metadata file")
    return info

def get_lookup(year: int, regen: bool = True) -> pd.DataFrame:
    if regen:
        info = get_metadata(year)
    else:
        info = pd.read_excel(f"data/pitcher_data/{str(year)}/{str(year)}_pitcher_metadata.xlsx")
    pitcher_ids = info["key_mlbam"]
    pitcher_name = info["name_last"] + "_" + info["name_first"]
    return {pitcher_ids[i] : pitcher_name[i] for i in range(len(pitcher_ids))}

def get_all_data(season_list: [[str, str]], cull_vars: [str], force_regen: bool = False) -> None:
    for season in season_list:
        th.Thread(target=get_season_data, args=(season, cull_vars, force_regen)).start() # split workers to each year

def get_season_data(season: [str, str], cull_vars: [str], force_regen: bool = False) -> None:
    # get look up table for names/ids
    year = int(season[0][:4])
    lookup = get_lookup(year, False) #switch to True to regen data
    for id in lookup.keys():
        th.Thread(target=get_pitcher_data, args=(season, id, lookup, cull_vars, force_regen)).start() #split off into per query workers
        # sleep(0.5) # prevent rate limit if needed

def get_pitcher_data(season: [str, str], id: int, lookup: dict, cull_vars: [str], force_regen: bool = False) -> None:
    path = f"data/pitcher_data/{season[0][:4]}/{lookup[id]}.xlsx"
    if os.path.exists(path) and not force_regen:
        print(f"file {path} exists, passing")
        return 0
    data = cull_data(pyb.statcast_pitcher(season[0], season[1], id), cull_vars)
    if not os.path.exists(path) or force_regen:
        data.to_excel(path)
        print(f"wrote {path}")
        
def get_missing() -> {str : [str]}:
    missing = {}
    for year in os.listdir("data/pitcher_data"):
        lookup = get_lookup(year, False)
        missing.update({year:[]})
        for id in lookup.keys():
            path = f"data/pitcher_data/{year}/{lookup[id]}.xlsx"
            if not os.path.exists(path):
                missing.update({year : missing[year] + [lookup[id]]})
    return missing

"""
# get the preliminary metadata loaded into variables:

pitcher_info = pd.read_excel("data/pitcherinfo.xlsx")

pitcher_ids = pitcher_info["key_mlbam"]
pitcher_name= pitcher_info["name_last"] + "_" + pitcher_info["name_first"]

# lookup table that converts MLBAM id's to last_first name
lookup = {pitcher_ids[i] : pitcher_name[i] for i in range(len(pitcher_ids))}
"""