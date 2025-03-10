import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels.stats.weightstats as sm
import datapullhelper as dp
import datacalchelper as dc
import dataparse as parse
import threading as th

def get_s_values(name: str, year) -> pd.DataFrame:
    smean = pd.read_excel("data/calcs/save_calcs/global_mean_data.xlsx", index_col=0)[year]
    sstd = pd.read_excel("data/calcs/save_calcs/global_std_data.xlsx", index_col=0)[year]
    player_data = pd.read_excel(f"data/save_data/{year}/{name}.xlsx", index_col=0)
    player_data = player_data.loc[player_data["IF"] == 9].loc[player_data["I0"] != 1].set_index("date").T
    if len(player_data.columns) == 0:
        return -1
    # print(player_data.T)
    out_df = get_s_vals_one_game(player_data[player_data.columns[0]], smean, sstd).rename(player_data.columns[0]).to_frame()
    for date in player_data.columns[1:]:
        out_df = out_df.join(get_s_vals_one_game(player_data[date], smean, sstd).rename(date))
    
    s_tots = {}
    for col in out_df.columns:
        col_data = out_df[col]
        s_tots.update({col: col_data.sum()})
    out_df = out_df.T.join(pd.Series(s_tots).rename("total")).T
    out_df.T.to_excel(f"data/s_vals/{year}/{name}_s_val_data.xlsx")
    print(f"done sval {year} {name}")
    return out_df.T["total"]

def get_s_vals_one_game(game_data, smean, sstd):
    pos_vars = ["TB"] #want lower, so left
    neg_vars = ["dS0", "dSF", "K", "IP"] #want higher, so right
    
    s_val_dict = {"TB": get_s_vals_one_stat(game_data["TB"], smean["TB"], sstd["TB"], "smaller")}
    for var in neg_vars:
        s_val_dict.update({var: get_s_vals_one_stat(game_data[var], smean[var], sstd[var], "larger")})
    s_val_dict = pd.Series(s_val_dict)
    return s_val_dict
    
    
def get_s_vals_one_stat(stat_data: pd.Series, mean, std, side):
    p_val = sm._zstat_generic(stat_data, mean, std, side)[1]
    s_val = 1/p_val - 1
    return s_val