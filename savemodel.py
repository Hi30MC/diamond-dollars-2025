import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels.stats.weightstats as sm
import datapullhelper as dp
import datacalchelper as dc
import dataparse as parse
import threading as th

#conglomerate files

def get_save_data_year_file(year: [int]) -> pd.DataFrame:
    paths = dp.get_all_files_in_directory(f"data/save_data/{year}")
    out_df = pd.concat([pd.read_excel(file, index_col=0) for file in paths], axis=0)
    out_df = out_df.loc[(out_df["I0"] != 1) & (out_df["IF"] == 9)]

    # gen mean row
    
    means = pd.DataFrame([{col : out_df[col].mean() for col in out_df.columns[1:]}])
    
    # gen std row
    
    stds = pd.DataFrame([{col : out_df[col].std() for col in out_df.columns[1:]}])
    
    # tack on both to bottom
    
    df = pd.concat([out_df, means, stds], ignore_index = True, axis=0)
    df.to_excel(f'data/calcs/save_calcs/{year}_conglomerate_mu_std.xlsx')
    return df

def get_save_data_global(years: [int]) -> pd.DataFrame:
    out_df = pd.read_excel(f"data/calcs/save_calcs/{years[0]}_conglomerate_mu_std.xlsx", index_col=0).tail(2).drop("date", axis=1)
    out_df.index = [f"mu {years[0]}", f"std {years[0]}"]
    for year in years[1:]:
        data = pd.read_excel(f"data/calcs/save_calcs/{year}_conglomerate_mu_std.xlsx", index_col=0).tail(2).drop("date", axis=1)
        data.index = [f"mu {year}", f"std {year}"]
        out_df = pd.concat([out_df, data], axis=0)
    out_df.to_excel("data/calcs/save_calcs/global_conglomerate_mu_std.xlsx")
    return out_df

def get_s_vals(path: str, means: pd.Series, stds: pd.Series) -> pd.DataFrame:
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
            s_vals = get_s_vals(path, year_metadata.loc["mu"], year_metadata.loc["std"])
            if type(s_vals) != int:
                s_vals.to_excel(f"data/s_vals/{year}/{dp.path_to_name(path)}.xlsx")
      
def get_series_summary(s: pd.Series) -> pd.Series:
    median, iqr = s.median(), s.quantile(0.75) - s.quantile(0.25)
    max = s.quantile(0.75) + 1.5 * iqr
    filtered = s.loc[s < max]
    mean = filtered.mean()
    std = filtered.std()
    return pd.Series({'median': median, "IQR": iqr, "Upper Inner Fence": max, "mu": mean, "std": std})
    
def get_s_val_meta(years: [int]) -> pd.DataFrame:
    df = pd.concat([get_series_summary(pd.Series([x for y in [pd.read_excel(path)["sum"].values for path in dp.get_all_files_in_directory(f"data/s_vals/{year}")] for x in y])).rename(year) for year in years], axis=1).T
    df.to_excel("data/calcs/save_calcs/s_val_mu_std.xlsx")
    return df
    
def update_s_val_sheets(years: [int]) -> None:
    meta = pd.read_excel("data/calcs/save_calcs/s_val_mu_std.xlsx", index_col=0)[["mu", "std"]].T
    for year in years:
        paths = dp.get_all_files_in_directory(f"data/s_vals/{year}")
        yr_mu = meta[int(year)]["mu"]
        yr_std = meta[int(year)]["std"]
        for path in paths:
            data = pd.read_excel(path, index_col=0)
            data["Save"] = [1 if x > yr_mu+yr_std else 0 for x in data["sum"]]
            data.to_excel(path)
            
def get_s_val_master_sheet(years: [int]) -> None:   
    master_sheet = pd.concat([pd.Series({dp.path_to_name(path): pd.read_excel(path)["Save"].sum() for path in dp.get_all_files_in_directory(f"data/s_vals/{year}")}).rename(f"{year} Saves") for year in years] + [pd.Series({dp.path_to_name(path): len(pd.read_excel(path)["Save"]) for path in dp.get_all_files_in_directory(f"data/s_vals/{year}")}).rename(f"{year} Save Chances") for year in years], axis=1).fillna(0)
    # gen mean row
    
    means = pd.DataFrame([{col : master_sheet[col].mean() for col in master_sheet.columns}])
    means.index = ["mean"]
    
    # gen std row
    
    totals = pd.DataFrame([{col : master_sheet[col].sum() for col in master_sheet.columns}])
    totals.index = ["total"]
    
    master_sheet = pd.concat([master_sheet, means, totals], axis=0)
    master_sheet.to_excel("data/model/save_counts.xlsx")
    return None