""" fold_selection.py
    creates a json file containing the data indices for each fold.
    each fold contains 20% of the data

    - The sampling is stratified by the target variable.
    - The random seed is set to 42.

Input:
  - data/diabetia.csv
Output:
  - data/fold_selection-{diagnostic}.json
Additional outputs:
  - None
"""

# get complication from command line ------------------------------------------
from conf.global_constants import DIAGNOSTIC

# Constants -------------------------------------------------------------------
IN_PATH = 'data/diabetia.csv'
OUT_PATH = f"data/fold_selection-{DIAGNOSTIC}.json"

# Import libraries ------------------------------------------------------------

# Code: fold selection --------------------------------------------------------
# general code to make stratified folds given the selected diagnostic