import pandas as pd
import datapullhelper as dp
import datacalchelper as dc
import os
import pybaseball as pyb
import threading as th
from timeit import default_timer as dt

# Save

def write_save_files(years: [str]) -> [th.Thread]:
    threadlist = []
    for year in years:
        t = th.Thread(target=write_save_files_in_year, args=(year,))
        t.start()
        threadlist.append(t)
    return threadlist

def write_save_files_in_year(year: str) -> None:
    files = dp.get_all_files_in_directory(f"data/pitcher_data/{year}")
    for i, file in [*enumerate(files)][1:]:
        t = convert_to_save(file)
        t.to_excel(f"data/save_data/{year}/{file[:-5].split("/")[-1]}.xlsx")
        print(f"done save {year} {i}")
    print(f"done save {year}")

def convert_to_save(file_path:str) -> pd.DataFrame():
    df = pd.read_excel(file_path)
    dates = dc.get_game_dates(df)
    TB = dc.get_TB_per_game(df)
    PC = dc.get_pitch_count_per_game(df)
    dS0 = dc.get_init_score_differential_per_game(df)
    dSF = dc.get_final_score_differential_per_game(df)
    d2S = dSF - dS0
    K = dc.get_strikeout_count_per_game(df)
    IP = dc.get_innings_pitched_per_game(df)
    I0 = dc.get_inning_per_game(df, True)
    IF = dc.get_inning_per_game(df, False)
    
    return pd.DataFrame({"TB": TB, "PC": PC, "dSF": dSF, "d2S": d2S, "K": K, "IP": IP, "I0": I0, "IF" : IF}, index=dates).reset_index(names="date")

# relief

def write_relief_files(years: [str]) -> [th.Thread]:
    threadlist = []
    for year in years:
        t = th.Thread(target=write_relief_files_in_year, args=(year,))
        t.start()
        threadlist.append(t)
    return threadlist

def write_relief_files_in_year(year: str) -> None:
    print(pyb.pitching_stats(year)["name","ERA"])
    t0 = dt()
    files = dp.get_all_files_in_directory(f"data/pitcher_data/{year}")
    out = pd.Series()
    k = 1
    while out.empty:
        out = convert_to_relief(files[k], k, year).rename(files[k][:-5].split("/")[-1]).to_frame()
        k += 1
    for i, file in [*enumerate(files)][k+1:]:
        d = convert_to_relief(file, i, year).rename(file[:-5].split("/")[-1]).to_frame()
        if not d.empty:
            out = out.join(d)
        if i % 50 == 0:
            print(dt()-t0)
    
    pd.concat([out.T.reset_index(names="name"), pyb.pitching_stats(year)["ERA"]]).to_excel(f"data/relief_data/{year}_testing.xlsx")

def convert_to_relief(file_path: str, i: int, year: str) -> pd.Series():
    df = pd.read_excel(file_path, index_col=0).set_index("game_date")
    valid_games = []
    for date in dc.get_game_dates(df.reset_index()):
        if dc.get_inning(df.reset_index(), date, True) != 1:
            valid_games.append(date)
    df = df.loc[valid_games].reset_index()
    if df.empty:
        return pd.Series()

    # dates = dc.get_game_dates(df)
    # TBpg = dc.get_TB_avg(df)
    # Kpg = dc.get_play_avg(df, "strikeout")
    # flyoutpg = dc.get_play_avg(df, "fly_out")
    # walkpg = dc.get_play_avg(df, "walk")
    ERA = dc.get_era_season(df)
    # chasePpg = dc.get_chase_percent_season(df)
    # strikepg = dc.get_strike_count_avg(df)
    # dS0pg = dc.get_init_score_differential_avg(df)
    # dSFpg = dc.get_final_score_differential_avg(df)
    # d2Spg = dSFpg - dS0pg
    # num_games = dc.get_game_count(df)

    print(f"finished relief {year} {i}")
    return pd.Series({"ERA": ERA})
    # return pd.Series({"ERA": ERA, "TB/G": TBpg, "K/G": Kpg, "fly_out/G": flyoutpg, "walk/G": walkpg, "chase%/G": chasePpg, "strike/G": strikepg, "d2S/G": d2Spg, "GP": num_games})

# Global statistic calc (relief) save to data/relief_data/global_mean_data (rows are years)

def gen_relief_mean_data(years: [str]) -> pd.DataFrame:
    out = gen_relief_mean_data_year(years[0]).rename(years[0]).to_frame()
    for year in years[1:]:
        row = gen_relief_mean_data_year(year).to_frame()
        if not row.empty():
            out = out.join(row)
    global_stats = out.T
    global_means = {}
    for col in global_stats.columns:
        col_data = global_stats[col]
        global_means.update({col: col_data.mean()})
    global_stats = global_stats.T.join(pd.Series(global_means).rename("mean")).T
    global_stats.to_excel(f"data/calcs/relief_calcs/global_mean_data.xlsx")
    return global_stats
    
def gen_relief_mean_data_year(year: str) -> pd.Series:
    data = pd.read_excel(f"data/relief_data/{year}.xlsx")
    means = {}
    for column in data.columns[2:]:
        col_data = data.pop(column)
        print(col_data)
        means.update({column: col_data.mean()})
    return pd.Series(means).rename(year)

# Per-pitcher statistic calc (save_data) save to data/save_data/year/year_mean_data.xlsx (final row should be full mean)

def gen_save_mean_data(years: [str]) -> pd.DataFrame:
    out = gen_save_mean_data_year(years[0]).to_frame()
    for year in years[1:]:
        out = out.join(gen_save_mean_data_year(year).to_frame())
    global_stats = out.T
    global_means = {}
    for col in global_stats.columns:
        col_data = global_stats[col]
        global_means.update({col: col_data.mean()})
    global_stats = global_stats.T.join(pd.Series(global_means).rename("mean")).T
    global_stats.T.to_excel(f"data/calcs/save_calcs/global_mean_data.xlsx")
    return global_stats

def gen_save_mean_data_year(year: str) -> pd.Series:
    lookup = dp.get_lookup(year, regen=False)
    init_data = pd.read_excel(f"data/save_data/{year}/{[*lookup.values()][0]}.xlsx")
    yf = gen_save_mean_data_player(init_data.loc[init_data["IF"] == 9]).rename([*lookup.values()][0]).to_frame()

    for name in [*lookup.values()][1:]:
        data = pd.read_excel(f"data/save_data/{year}/{name}.xlsx")
        data = data.loc[data["IF"] == 9]
        if len(data["TB"]) == 0:
            continue
        col = gen_save_mean_data_player(data).rename(name).to_frame()
        if name in yf.columns:
            continue
        yf = yf.join(col)
    yf = yf.T
    year_means = {}
    for col in yf.columns:
        col_data = yf[col]
        year_means.update({col: col_data.mean()})
    yf = yf.T.join(pd.Series(year_means).rename("mean")).T
    yf.to_excel(f"data/calcs/save_calcs/{year}_mean_data.xlsx")
    return yf.T["mean"].rename(year)

def gen_save_mean_data_player(data: pd.DataFrame) -> pd.Series:
    means = {}
    for column in data.columns[2:]:
        col_data = data.pop(column)
        means.update({column: col_data.mean()})
    return pd.Series(means)

# stds

def gen_global_stds_file(years: [str]) -> pd.DataFrame:
    stds = gen_save_std_season(years[0]).to_frame()
    for year in years[1:]:
        stds = stds.join(gen_save_std_season(year).to_frame())
    stds.to_excel(f"data/calcs/save_calcs/global_std_data.xlsx")
    return stds

def gen_save_std_season(year: str) -> pd.Series:
    lookup = dp.get_lookup(year, regen=False)
    init_data = pd.read_excel(f"data/save_data/{year}/{[*lookup.values()][0]}.xlsx", index_col=0)
    combined_data = init_data.loc[init_data["IF"] == 9][[*init_data.columns[1:]]].T
    for i, name in enumerate([*lookup.values()][1:]):
        print(f"done std {year} {name}")
        p = pd.read_excel(f"data/save_data/{year}/{name}.xlsx", index_col=0)
        combined_data = combined_data.join(p.loc[p["IF"] == 9][[*p.columns[1:]]].T, lsuffix=name+str(i))
    combined_data = combined_data.T.reset_index()

    stds = {}
    for column in combined_data.columns[1:]:
        col_data = combined_data.pop(column)
        stds.update({column: col_data.std()})
    stds = pd.Series(stds).rename(f"{year}")    
    
    return stds

