import pybaseball as pyb
import pandas as pd

pitcher_info = pd.read_excel("data/pitcherinfo.xlsx")

pitcher_ids = pitcher_info["key_mlbam"]
pitcher_name= pitcher_info["name_last"] + "_" + pitcher_info["name_first"]

# lookup table that converts MLBAM id's to last_first name
lookup = {pitcher_ids[i] : pitcher_name[i] for i in range(len(pitcher_ids))}

"""
Season Dates:

2021: Apr 1 - Nov 2 
2022: Apr 7 - Nov 5
2023: Mar 30 - Nov 1
2024: Mar 20 - Oct 30

All-encompassing dates:

Feb 14 - Dec 25 (these are arbitrary)
"""

season_list = [[j + "-02-14", j+ "-12-25"] for j in [str(i) for i in range(2021, 2025)]]

for season in season_list:
    for id in pitcher_ids:
        data = pyb.statcast_pitcher(season[0], season[1], id)
        path = "data/pitcher_data/" + season[0][:4] + "/"+lookup[id] + ".xlsx"
        data.to_excel(path)