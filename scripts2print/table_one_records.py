""" 
table_one_records.py
    This file contains the functions to create table one bases on records

Input:
  - data/diabetia.csv
Output:
  - data/table_one_records.csv
Additional outputs:
  - None
"""

# get complication from command line ------------------------------------------
import os
import sys
ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)
from libs.logging import logging

# Constants
IN_PATH = 'data/diabetia.csv'
OUT_PATH = 'data/table_one_records.csv'
CONFIG_PATH = 'conf/columnGroups.json'

# Import libraries
import pandas as pd
import numpy as np
import json
import re

#..Default configurations


def run():
    """Function to run all process requiered to create table one based on patients"""
    pass


if __name__ == '__main__':
    logging.info(f'{"="*30}RECORDS TABLE ONE STARTS')
    run()
    logging.info(f'{"="*30}RECORDS TABLE ONE FINISHED')