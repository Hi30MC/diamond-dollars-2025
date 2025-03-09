import pandas as pd
import datapullhelper as dp

# metadata utils

def get_game_count(df: pd.DataFrame) -> int:
    return len(get_game_dates(df))

def get_game_dates(df: pd.DataFrame) -> [str]:
    return df["game_date"].unique()

def get_culled_df(df: pd.DataFrame, date: str) -> pd.DataFrame:
    return df.loc[df["game_date"] == date]

def get_year(df: pd.DataFrame) -> str:
    return df["game_date"].iloc[0][:4]

# stat utils

# ERA
def get_era(df: pd.DataFrame, date: str) -> float:
    day_df = get_culled_df(df, date)
    score_col = "home_score" if day_df["inning_topbot"].iloc[0] == "Bot" else "away_score"
    score_diff = day_df[score_col].iloc[0] - day_df[score_col].iloc[-1]
    inning_diff = day_df["inning"].iloc[0] - day_df["inning"].iloc[-1]+1
    return score_diff / inning_diff * 9

def get_era_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_era(df, date)})
    return pd.Series(data)

def get_era_season(df: pd.DataFrame) -> float:
    return get_era_per_game(df).mean()

# play type grabber

def get_play(df: pd.DataFrame, date: str, play: str) -> int:
    if play == "fly_out":
        day_df = get_culled_df(df, date).loc[(df["events"] == "field_out") & ((df["bb_type"] == "fly_ball") | (df["events"] == "popup"))]
        return len(day_df)
    else:
        day_df = get_culled_df(df, date).loc[df["events"] == play]
        return len(day_df)
    
def get_play_per_game(df: pd.DataFrame, play: str) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_play(df, date, play)})
    return pd.Series(data)

def get_play_tot(df: pd.DataFrame, play: str) -> int:
    return get_play_per_game(df, play).sum()

def get_play_avg(df: pd.DataFrame, play: str) -> float:
    return get_play_per_game(df, play).mean()

# Chase
def get_chase(df: pd.DataFrame, date: str) -> int:
    day_df = get_culled_df(df, date).loc[df["description"] == "swinging_strike"].loc[df["zone"] > 9]
    return len(day_df)

def get_chase_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_chase(df, date)})
    return pd.Series(data)

def get_chase_percent_per_game(df: pd.DataFrame) -> pd.Series:
    chase_count = get_chase_per_game(df)
    strike_count = get_strike_count_per_game(df)
    return chase_count / strike_count

def get_chase_percent_season(df: pd.DataFrame) -> float:
    return get_chase_percent_per_game(df).mean()

# K
def get_strike_count(df: pd.DataFrame, date: str) -> int:
    day_df = get_culled_df(df, date).loc[df["type"] == "S"].loc[df["description"] != "foul"]
    return len(day_df)

def get_strike_count_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_strike_count(df, date)})
    return pd.Series(data)

def get_strike_count_avg(df: pd.DataFrame) -> float:
    return get_strike_count_per_game(df).mean()

# TB
def get_TB(df: pd.DataFrame, date: str) -> int: 
    tb = 0
    day_data = get_culled_df(df, date)["events"].value_counts()
    for play, weight in zip("single double triple home_run".split(), [1, 2, 3, 4]):
        if play in day_data.keys():
            tb += day_data[play] * weight
    return tb

def get_TB_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_TB(df, date)})   
    return pd.Series(data)

def get_TB_tot(df: pd.DataFrame) -> int:
    return get_TB_per_game(df).sum()

def get_TB_avg(df: pd.DataFrame) -> float:
    return get_TB_per_game(df).mean()


# PC
def get_pitch_count(df: pd.DataFrame, date: str) -> int:
    day_df = get_culled_df(df, date) 
    return len(day_df)
    
def get_pitch_count_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_pitch_count(df, date)})
    return pd.Series(data)

def get_pitch_count_tot(df: pd.DataFrame) -> int:
    return get_pitch_count_per_game(df).sum()

# dS0

def get_init_score_differential(df: pd.DataFrame, date: str) -> int:
    day_df = get_culled_df(df, date)[["inning_topbot", "home_score", "away_score"]].iloc[-1]
    dS = day_df["home_score"] - day_df["away_score"]
    dS = dS if day_df["inning_topbot"] == "Top" else -1 * dS
    return dS
    
def get_init_score_differential_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_init_score_differential(df, date)})
    return pd.Series(data)

def get_init_score_differential_tot(df: pd.DataFrame) -> int:
    return get_init_score_differential_per_game(df).sum()

def get_init_score_differential_avg(df: pd.DataFrame) -> float:
    return get_init_score_differential_per_game(df).mean()

# dSF

def get_final_score_differential(df: pd.DataFrame, date: str) -> int:
    day_df = get_culled_df(df, date)[["inning_topbot", "home_score", "away_score"]].iloc[0]
    dS = day_df["home_score"] - day_df["away_score"]
    dS = dS if day_df["inning_topbot"] == "Top" else -1 * dS
    return dS
    
def get_final_score_differential_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_final_score_differential(df, date)})
    return pd.Series(data)

def get_final_score_differential_tot(df: pd.DataFrame) -> int:
    return get_final_score_differential_per_game(df).sum()

def get_final_score_differential_avg(df: pd.DataFrame) -> int:
    return get_final_score_differential_per_game(df).mean()

# IP

def get_innings_pitched(df: pd.DataFrame, date: str) -> int:
    day_df = get_culled_df(df, date)["inning"]
    return day_df.iloc[0]-day_df.iloc[-1] + 1
    
def get_innings_pitched_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_innings_pitched(df, date)})
    return pd.Series(data)

def get_innings_pitched_tot(df: pd.DataFrame) -> int:
    return get_innings_pitched_per_game(df).sum()


"""

example quadruplet

def get_stat(df: pd.DataFrame, date: str) -> type:
    day_df = get_culled_df(df, date) 
    return len(day_df)
    
def get_stat_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)
    data = {}
    for date in dates:
        data.update({date : get_stat(df, date)})
    return pd.Series(data)

def get_stat_tot(df: pd.DataFrame) -> type:
    return get_stat_per_game(df).sum()
    
def get_stat_avg(df: pd.DataFrame) -> type:
    return get_stat_per_game(df).mean()
"""

