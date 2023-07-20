""" fold_selection.py
    creates a json file containing the data indices for each fold.
    each fold contains 20% of the data

    - The sampling is stratified by the target variable.
    - The random seed is set to 42.

Input:
  - data/diabetia.csv
Output:
  - data/fold_selection-{complication}.json
Additional outputs:
  - None
"""

# get complication from command line
import sys
COMPLICATION = sys.argv[1]
if not COMPLICATION in ['E112','E113','E114','E115']:
    raise ValueError('given complication must be one of E112, E113, E114, E115')

# Constants
IN_PATH = 'data/diabetia.csv'
OUT_PATH = f"data/fold_selection-{COMPLICATION}.json"

# Import libraries