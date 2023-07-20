""" enginering.py
    This file contains the functions for data cleaning and feature enginering.
    - remove unnecessary columns
    - one-hot encoding (if needed)

Input:
  - data/hk_database.csv
Output:
  - data/hk_database_cleaned.csv
Additional outputs:
  - None
"""

# Constants
IN_PATH = 'data/hk_database.csv'
OUT_PATH = 'data/hk_database_cleaned.csv'

# Import libraries