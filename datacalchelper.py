import pandas as pd
import datapullhelper as dp

def get_game_count(df: pd.DataFrame) -> int:
    return len(get_game_dates(df))

def get_game_dates(df: pd.DataFrame) -> [str]:
    return df["game_date"].unique()

# todo: ERA per game and per season, chase, chase%, 

def get_culled_df(df: pd.DataFrame, date: str) -> pd.DataFrame:
    return df.loc[df["game_date"] == date]


def get_era_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)

    data = {}
    for date in dates:
        day_df = get_culled_df(df, date)
        if len(day_df) == 0:
            continue
        score_col = "home_score" if day_df["inning_topbot"].iloc[0] == "Top" else "away_score"
        score_diff = day_df[score_col].iloc[0] - day_df[score_col].iloc[-1]
        inning_diff = day_df["inning"].iloc[0] - day_df["inning"].iloc[-1]+1
        data.update({date : score_diff / inning_diff * 9})
    return pd.Series(data)

def get_era_season(df: pd.DataFrame) -> float:
    return get_era_per_game(df).mean()

def get_chase_per_game(df: pd.DataFrame) -> pd.Series:
    dates = get_game_dates(df)

    data = {}
    for date in dates:
        day_df = get_culled_df(df, date).loc[df["description"] == "swinging_strike"].loc[df["zone"] > 9]
        if len(day_df) == 0:
            continue
        data.update({date : len(day_df["inning_topbot"])})
    return pd.Series(data)