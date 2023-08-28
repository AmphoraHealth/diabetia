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
ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging

# Constants
IN_PATH = 'data/diabetia.csv'
OUT_PATH = 'data/table_one_records.csv'
CONFIG_PATH = 'conf/columnGroups.json'
CONFIG_TABLEONE_PATH = 'scripts2print/aux_table_one/config_tableone.json'

# Import libraries
import pandas as pd
import numpy as np
import json
import re
from aux_table_one import TableOne


def run():
    """
    Function to run all process requiered to create table one based on patients
    """
    try:
      """
      first_group = TableOne(df,filter)
      second_group = TableOne(df,filter)
      third_group = TableOne(df,filter)

      first_group.run()
      second_group.run()
      third_group.run()

      data = concat(first_group,second_group)
      data = concat(data,third_group
      """
      #..Read data and config files
      data = pd.read_csv(IN_PATH,low_memory=False, nrows=None)
      config = json.load(open(CONFIG_TABLEONE_PATH, 'r',encoding='utf-8'))

      #..All patients
      all_records = TableOne(
          data=data,
          name = 'All records'
        )
      all_records_frame = all_records.create()

      #..Without T2D
      wo_t2d = TableOne(
        data = data[data['diabetes_mellitus_type_2']==0],
        name = 'Records without T2D'
        )
      wo_t2d_frame = wo_t2d.create()

      #..With T2D WO complications
      t2d_wo_complications = TableOne(
        data = data[
          (data['diabetes_mellitus_type_2']==1) &\
          (data[config['categories']['t2d_complications'].keys()].sum(axis=1)<=0)
          ],
        name = 'Records with T2D w/o complications'
      )
      t2d_wo_complications_frame = t2d_wo_complications.create()

      #..With T2D with complications
      t2d_with_complications = TableOne(
        data = data[
          (data['diabetes_mellitus_type_2']==1) &\
          (data[config['categories']['t2d_complications'].keys()].sum(axis=1)>0)
          ],
        name = 'Records with T2D with complications'
      )
      t2d_with_complications_frame = t2d_with_complications.create()

      #..Final table one
      finalTableOne = pd.concat(
        [
          all_records_frame.set_index(['name','category']),
          wo_t2d_frame.set_index(['name','category']),
          t2d_wo_complications_frame.set_index(['name','category']),
          t2d_with_complications_frame.set_index(['name','category'])
        ],
        axis=1
      )
      finalTableOne.reset_index(inplace=True)
      logging.info('Table one created')

    except Exception as e:
      raise logging.error(f'Run process to create table one failed. {e}')

    return finalTableOne


if __name__ == '__main__':
    logging.info(f'{"="*30}RECORDS TABLE ONE STARTS')
    data = run()
    data.to_csv(OUT_PATH,index=False)
    logging.info(f'{"="*30}RECORDS TABLE ONE FINISHED')