""" 
table_one_records.py
    This file contains the functions to create table one bases on patients

Input:
  - data/diabetia.csv
Output:
  - data/table_one_patients.csv
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
OUT_PATH = 'data/supplementary_material/table_one/table_one_patients.csv'
CONFIG_PATH = 'conf/columnGroups.json'
CONFIG_TABLEONE_PATH = 'scripts2print/aux_table_one/config_tableone.json'

# Import libraries
import pandas as pd
import numpy as np
import json
import re
from aux_table_one import TableOne
from aux_table_one import SummarizeData
from aux_table_one import CreateGlucose

#..Default configurations


def run():
    """
    Function to run all process requiered to create table one based on patients
    """
    try:
      
      #..Read data and config files
      data = pd.read_csv(IN_PATH,low_memory=False, nrows=None)
      config = json.load(open(CONFIG_TABLEONE_PATH, 'r',encoding='utf-8'))

      #..Adding auxiliar column of glucose composed by 4 mean glucose target cols
      createGlucose = CreateGlucose(data = data)
      data['glucose_value_mean'] = createGlucose.create()

      #..prepocess of data to keep only a summarized table by patient
      summarize = SummarizeData(
        data = data,
        config_path=CONFIG_TABLEONE_PATH
      )
      data = summarize.transform()

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
          (data[config['categories']['t2d_complications']['columnsUsed']].sum(axis=1)<=0)
          ],
        name = 'Records with T2D w/o complications'
      )
      t2d_wo_complications_frame = t2d_wo_complications.create()

      #..With T2D with complications
      t2d_with_complications = TableOne(
        data = data[
          (data['diabetes_mellitus_type_2']==1) &\
          (data[config['categories']['t2d_complications']['columnsUsed']].sum(axis=1)>0)
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
    logging.info(f'{"="*30}PATIENTS TABLE ONE STARTS')
    data = run()
    data.to_csv(OUT_PATH,index=False)
    logging.info(f'{"="*30}PATIENTS TABLE ONE FINISHED')