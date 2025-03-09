import pandas as pd
import datapullhelper as dp
import datacalchelper as dc
import os
import pybaseball as pyb
import threading as th
from timeit import default_timer as dt

# Save

def write_save_files(years: [str]) -> None:
    for year in years:
        th.Thread(target=write_save_files_in_year, args=(year,)).start()

def write_save_files_in_year(year: str) -> None:
    files = dp.get_all_files_in_directory(f"data/pitcher_data/{year}")
    for i, file in [*enumerate(files)][1:]:
        t = convert_to_save(file)
        t.to_excel(f"data/save_data/{year}/{file.split(".")[0].split("/")[-1]}.xlsx")
        print(f"done save {year} {i}")
    print(f"done save {year}")

def convert_to_save(file_path:str) -> pd.DataFrame():
    df = pd.read_excel(file_path)
    dates = dc.get_game_dates(df)
    TB = dc.get_TB_per_game(df)
    PC = dc.get_pitch_count_per_game(df)
    dS0 = dc.get_init_score_differential_per_game(df)
    dSF = dc.get_init_score_differential_per_game(df)
    K = dc.get_strike_count_per_game(df)
    IP = dc.get_innings_pitched_per_game(df)
    I0 = dc.get_inning_per_game(df, True)
    IF = dc.get_inning_per_game(df, False)
    
    return pd.DataFrame({"TB": TB, "PC": PC, "dS0": dS0, "dSF": dSF, "K": K, "IP": IP, "I0": I0, "IF" : IF}, index=dates).reset_index(names="date")

# relief

def write_relief_files(years: [str]) -> None:
    for year in years:
        th.Thread(target=write_relief_files_in_year, args=(year,)).start()

def write_relief_files_in_year(year: str) -> None:
    t0 = dt()
    files = dp.get_all_files_in_directory(f"data/pitcher_data/{year}")
    out = convert_to_relief(files[1], 1, year).rename(files[1].split(".")[0].split("/")[-1]).to_frame()
    for i, file in [*enumerate(files)][2:]:
        d = convert_to_relief(file, i, year).rename(file.split(".")[0].split("/")[-1]).to_frame()
        out = out.join(d)
        if i % 50 == 0:
            print(dt()-t0)
            
    # parallelization: not really necessary here so not used
    
    # threadlist = []
    # for i, file in [*enumerate(files)][2:]:
        # t = th.Thread(target=lambda out, file, i: out.join(convert_to_relief(file, i).rename(file.split(".")[0].split("/")[-1])), args=(out,file, i))
        # t.start
        # threadlist.append(t)
    # for i, t in enumerate(threadlist):
        # t.join()
        # if i % 50 == 0:
        #     print(dt()-t0)
        
    out.T.reset_index(names="date").to_excel(f"data/relief_data/{year}.xlsx")

def convert_to_relief(file_path: str, i: int, year: str) -> pd.Series():
    df = pd.read_excel(file_path)
    dates = dc.get_game_dates(df)
    TBpg = dc.get_TB_avg(df)
    Kpg = dc.get_play_avg(df, "strikeout")
    flyoutpg = dc.get_play_avg(df, "fly_out")
    walkpg = dc.get_play_avg(df, "walk")
    ERA = dc.get_era_season(df)
    chasePpg = dc.get_chase_percent_season(df)
    strikepg = dc.get_strike_count_avg(df)
    dS0pg = dc.get_init_score_differential_avg(df)
    dSFpg = dc.get_final_score_differential_avg(df)

    print(f"finished relief {year} {i}")
    return pd.Series({"ERA": ERA, "TB/G": TBpg, "K/G": Kpg, "fly_out/G": flyoutpg, "walk/G": walkpg, "chase%/G": chasePpg, "strike/G": strikepg, "dS0/G": dS0pg, "dSF/G": dSFpg})
