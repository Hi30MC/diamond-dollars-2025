import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels.stats.weightstats as sm
import datapullhelper as dp
import datacalchelper as dc
import dataparse as parse
import threading as th

# def get_s_values(name: str, year) -> pd.DataFrame:
#     smean = pd.read_excel("data/calcs/save_calcs/global_mean_data.xlsx", index_col=0)[year]
#     sstd = pd.read_excel("data/calcs/save_calcs/global_std_data.xlsx", index_col=0)[year]
#     player_data = pd.read_excel(f"data/save_data/{year}/{name}.xlsx", index_col=0)
#     player_data = player_data.loc[player_data["IF"] == 9].loc[player_data["I0"] != 1].set_index("date").T
#     if len(player_data.columns) == 0:
#         return -1
#     out_df = get_s_vals_one_game(player_data[player_data.columns[0]], smean, sstd).rename(player_data.columns[0]).to_frame()
#     for date in player_data.columns[1:]:
#         out_df = out_df.join(get_s_vals_one_game(player_data[date], smean, sstd).rename(date))
    
#     s_tots = {}
#     for col in out_df.columns:
#         col_data = out_df[col]
#         s_tots.update({col: col_data.sum()})
#     out_df = out_df.T.join(pd.Series(s_tots).rename("total")).T
#     out_df.T.to_excel(f"data/s_vals/{year}/{name}_s_val_data.xlsx")
#     print(f"done sval {year} {name}")
#     return out_df.T["total"]

# def get_s_vals_one_game(game_data: pd.Series, smean: float, sstd: float) -> pd.Series:
#     pos_vars = ["TB"] #want lower, so left
#     neg_vars = ["dS0", "dSF", "K", "IP"] #want higher, so right
    
#     s_val_series = {"TB": get_s_vals_one_stat(game_data["TB"], smean["TB"], sstd["TB"], "smaller")}
#     for var in neg_vars:
#         s_val_series.update({var: get_s_vals_one_stat(game_data[var], smean[var], sstd[var], "larger")})
#     s_val_series = pd.Series(s_val_series)
#     return s_val_series
    
    
# def get_s_vals_one_stat(stat_data: pd.Series, mean: float, std: float, side: str) -> float:
#     p_val = sm._zstat_generic(stat_data, mean, std, side)[1]
#     s_val = 1/p_val - 1
#     return s_val

# def get_s_values_conglomerated(year) -> pd.DataFrame:
#     file_list = dp.get_all_files_in_directory(f"data/s_vals/{year}")
#     out_df = pd.read_excel(file_list[0], index_col=0).T
#     for file in file_list[1:]:
#         player_data = pd.read_excel(file, index_col=0).T
#         out_df = out_df.join(player_data, lsuffix = file[:-5].split("/")[-1][:-11])
#     out_df.T.to_excel(f"data/s_vals/{year}_conglomerated_s_val_data.xlsx")
#     return out_df.T["total"].reset_index(drop=True)

#conglomerate files

def get_save_data_year_file(year):
    file_list = dp.get_all_files_in_directory(f"data/save_data/{year}")
    out_df = pd.concat([pd.read_excel(file, index_col=0) for file in file_list], axis=0)
    out_df = out_df.loc[(out_df["I0"] != 1) & (out_df["IF"] == 9)]

    # gen mean row
    
    means = pd.DataFrame([{col : out_df[col].mean() for col in out_df.columns[1:]}])
    
    # gen std row
    
    stds = pd.DataFrame([{col : out_df[col].std() for col in out_df.columns[1:]}])
    
    # tack on both to bottom
    
    df = pd.concat([out_df, means, stds], ignore_index = True, axis=0)
    df.to_excel(f'data/calcs/save_calcs/{year}_conglomerate_mu_std.xlsx')
    return df

def get_save_data_global(years):
    out_df = pd.read_excel(f"data/calcs/save_calcs/{years[0]}_conglomerate_mu_std.xlsx", index_col=0).tail(2).drop("date", axis=1)
    out_df.index = [f"mu {years[0]}", f"std {years[0]}"]
    for year in years[1:]:
        data = pd.read_excel(f"data/calcs/save_calcs/{year}_conglomerate_mu_std.xlsx", index_col=0).tail(2).drop("date", axis=1)
        data.index = [f"mu {year}", f"std {year}"]
        out_df = pd.concat([out_df, data], axis=0)
    out_df.to_excel("data/calcs/save_calcs/global_conglomerate_mu_std.xlsx")
    return out_df

def get_s_vals(path: str, means, stds) -> pd.DataFrame:
    data = pd.read_excel(path, index_col=0).set_index("date")
    data = data.loc[data["IF"] == 9].loc[data["I0"] != 1]
    if len(data["TB"]) == 0:
        return -1
    out =  pd.concat([pd.Series({"TB": 1/[*sm._zstat_generic(row["TB"], means["TB"], stds["TB"], "smaller")][1] - 1} | {stat: 1/[*sm._zstat_generic(row[stat], means[stat], stds[stat], "larger")][1]-1 for stat in "d2S K IP".split()} | {"Win" : 1 if row["dSF"] > 0 else 0}).rename(i) for i, row in data.iterrows()], axis=1).T
    sum = pd.Series({date: row.values[:-1].sum() for date,row in out.iterrows()}).rename("sum").to_frame()
    out = out.join(sum)
    return out

def write_s_vals(years: [str]) -> None:
    global_meta = pd.read_excel("data/calcs/save_calcs/global_conglomerate_mu_std.xlsx", index_col=0)
    for year in years:
        paths = dp.get_all_files_in_directory(f"data/save_data/{year}")
        year_metadata = global_meta.loc[[f"mu {year}", f"std {year}"]]
        year_metadata.index = ["mu", "std"]
        for path in paths:
            # print(year, dp.path_to_name(path))
            # print(get_s_vals("data/save_data/2021/abad_fernando.xlsx", year_metadata.loc["mu"], year_metadata.loc["std"]))
            s_vals = get_s_vals(path, year_metadata.loc["mu"], year_metadata.loc["std"])
            # print(s_vals)
            if type(s_vals) != int:
                s_vals.to_excel(f"data/s_vals/{year}/{dp.path_to_name(path)}.xlsx")
      
def get_series_summary(s: pd.Series) -> pd.Series:
    median, iqr = s.median(), s.quantile(0.75) - s.quantile(0.25)
    max = s.quantile(0.75) + 1.5 * iqr
    filtered = s.loc[s < max]
    mean = filtered.mean()
    std = filtered.std()
    return pd.Series({'median': median, "IQR": iqr, "Upper Inner Fence": max, "mu": mean, "std": std})
    
def get_s_val_meta(years) -> (float, float):
    df = pd.concat([get_series_summary(pd.Series([x for y in [pd.read_excel(path)["sum"].values for path in dp.get_all_files_in_directory(f"data/s_vals/{year}")] for x in y])).rename(year) for year in years], axis=1).T
    df.to_excel("data/calcs/save_calcs/s_val_mu_std.xlsx")