import pybaseball as pyb
import numpy as np
import pandas as pd
import statsmodels.stats.weightstats as sm
import datapullhelper as dp
import datacalchelper as dc
import dataparse as parse

# generate mean/std data per season into df, write to file

def write_mu_std(years: [str]) -> pd.DataFrame():
    year0_data = pd.read_excel(f"data/relief_data/{years[0]}.xlsx", index_col=0).set_index("name")
    out_df = pd.concat([pd.Series({col : year0_data[col].mean() for col in year0_data.columns}).rename(f"{years[0]} mu").to_frame(), pd.Series({col : year0_data[col].std() for col in year0_data.columns}).rename(f"{years[0]} std").to_frame()], axis=1)
    for year in years[1:]:
        year_data = pd.read_excel(f"data/relief_data/{year}.xlsx", index_col=0).set_index("name")
        means = pd.Series({col : year_data[col].mean() for col in year_data.columns}).rename(f"{year} mu")
        stds = pd.Series({col : year_data[col].std() for col in year_data.columns}).rename(f"{year} std")
        out_df = pd.concat([out_df, means, stds], axis=1)   
    out_df = out_df.T
    out_df.to_excel("data/calcs/relief_calcs/season_mu_std.xlsx")
    return out_df

def write_r_scores(years: [str]) -> None:
    global_meta = pd.read_excel("data/calcs/relief_calcs/season_mu_std.xlsx", index_col=0)
    for year in "2022 2023 2024".split():
        year_data = pd.read_excel(f"data/relief_data/{year}.xlsx", index_col=0).set_index("name")
        year_metadata = global_meta.loc[[f"{int(year)-1} mu", f"{int(year)-1} std"]]
        year_metadata.index = ["mu", "std"]
        means = year_metadata.loc["mu"]
        stds = year_metadata.loc["std"]
        out = pd.concat([pd.Series({"GP tot" : row["GP"]} | {stat : 1/[*sm._zstat_generic(row[stat], means[stat], stds[stat], "smaller")][1]-1 for stat in "ERA  TB/G fly_out/G walk/G".split()} | {stat : 1/[*sm._zstat_generic(row[stat], means[stat], stds[stat], "larger")][1]-1 for stat in "K/G d2S/G GP".split()}).rename(i) for i, row in year_data.iterrows()], axis=1).T
        out = out.join(pd.Series({name : sum(out.loc[name][1:]) for name in out.index}).rename("r_score"))
        out = out.loc[out["GP tot"]>10]
        out.to_excel(f"data/model/relief_model/{year}_r_scores.xlsx")
    return None