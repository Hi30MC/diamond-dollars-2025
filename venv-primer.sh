#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install pybaseball
python3 -m pip install statsmodels
python3 -m pip install openpyxl