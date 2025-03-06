from pybaseball import statcast_pitcher
import numpy as np
import pandas as pd
import statsmodels as sm

data = statcast_pitcher('2017-07-15', "2017-07-16", player_id = 519242)

data.to_excel('data/testing.xlsx')