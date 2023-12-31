"""
02a_data_normalization.py
  This file contains the code for data normalization and standardization.

Input:
  - data/diabetia_balanced.csv
  - conf/columnGroups.json
Output:
  - data/diabetia_normalized.csv
Additional outputs:
  - Pickle file
  - json file with col Names in pickle obj
"""

# prepare environment ---------------------------------------------------------
# get constants from command line
import os
import sys
import re
ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging
from libs.global_constants import *

# Constants -------------------------------------------------------------------
DB_PATH:str = f"{S01_BALANCING}.parquet"
OUT_PATH:str = f"{S02A_NORMALIZATION}.parquet"
_NORMALIZATION_METHOD:str = f"{NORMALIZATION_METHOD}"
OUT_PATH_NORMALIZER:str = f"{S02A_NORMALIZATION}.pkl"
OUT_PATH_NORMALIZER_JSON:str = f"{S02A_NORMALIZATION}.json"

# Import libraries ------------------------------------------------------------
import pandas as pd
import numpy as np
import os
import sys
import json
import pickle
from aux_02a_data_normalization import normalizers
from aux_00_common import *

# Code: data normalization ----------------------------------------------------

class DataNormalization:
    """
    This is class is to normalize and standardize data from diabetia. It is required to give
    two inputs: 
    - diabetia_balanced.csv
    - columnGroups.json

    With json file, dtypes of cols will be identify to process only continues data. In next versions
    process to categorical and binary cols may be upload. 
    """
    
    def __init__(
          self,
          data:pd.DataFrame,
          configFile:dict,
          ):
      
      self.data = data
      self.config = configFile
      self.columnsToTransform = []
      self.normalizer = None


    def mainNormalization(self):
       """
       Function to run all required process to normalize and scale data
       """
       try:
          #..Run process
          self.columnsIdentification()
          self.normalize()

          #..Filter categorical columns
          """Only ID string col is saved. Other string cols are removed"""
          categoricalCols:list[str] = [
              col for col in self.data.columns \
                if bool(re.match('^.*_label',str(col))) == True \
                or col == 'dx_age_e11_cat'
            ]
          self.data = self.data.loc[:,~self.data.columns.isin(categoricalCols)]
          logging.info(f'{len(categoricalCols)} categorical cols were dropped')
          
          #..Saving new file
          save_data(self.data, OUT_PATH)

       except Exception as e:
          return logging.warning(f'{self.mainNormalization.__name__} failed. {e}')
    
    
    def columnsIdentification(self):
      """
      Function to identify data types column values and update self.columns attribute
      """
      try: 
        #..Only consider continuos or numerical cols
        self.columnsToTransform = \
        self.config['measuresCols']\
        + self.config['drugsCols']\
        + [
           'birthdate',
           'years_since_dx',
           'count_cx_w',
           'age_at_wx',
           'age_at_wx_ordinal',
           'dx_age_e11',
           'dx_age_e11_ordinal'
           ]
        self.columnsToTransform = [col for col in self.columnsToTransform if col in self.data.columns]
        self.columnsToTransform = [col for col in self.columnsToTransform if bool(re.match('^.*_label$',str(col)))==False]
        self.columnsToTransform = [col for col in self.columnsToTransform if bool(re.match('^.*_ordinal$',str(col)))==False]

        #..identify cols with nulls or 0s
        EmptyCols:list[str] = self.data.columns[((self.data==0)|(self.data.isnull())).all()]
        self.columnsToTransform = [col for col in self.columnsToTransform if col not in EmptyCols]
        
        return logging.info(f'{len(self.columnsToTransform)} Columns indetified')
      
      except Exception as e:
         return logging.warning(f'{self.columnsIdentification.__name__} failed. {e}')
        

    def normalize(self):
       """
       Function to normalize by Yeo-Johnson
       """
       try:
          #..Initialize PowerTransformer
          normalizer = normalizers[_NORMALIZATION_METHOD]
          
          #..fitting transformer
          normalizer.fit(self.data[self.columnsToTransform])
          self.data[self.columnsToTransform] = normalizer.transform(self.data[self.columnsToTransform])

          #..Saving pickle
          save_data(normalizer, OUT_PATH_NORMALIZER)

          #..Saving columns normalized
          save_data({"columnsNormalized":self.columnsToTransform}, OUT_PATH_NORMALIZER_JSON)
          
          return logging.info(f'Data normalized')  
       
       except Exception as e:
          return logging.warning(f'{self.normalize.__name__} failed. {e}')
          
          
       

    def __str__(self):
       return f'Data normalization by {_NORMALIZATION_METHOD}'
    

def runDataNormalization():
  """
  Function to run data normaliaztion
  """
  #..Files
  data:pd.DataFrame = load_data(DB_PATH)
  columnGroups:dict = load_data(f'{ROOT_PATH}/conf/columnGroups.json')

  #..Initialize normalization and standardization
  dataNorm = DataNormalization(
     data = data,
     configFile = columnGroups
  )

  #..Run process
  dataNorm.mainNormalization()

  return logging.info('Normalization process finished')


if __name__=='__main__':
   logging.info(f'{"="*30} DATA NORMALIZATION STARTS')
   runDataNormalization()
   logging.info(f'{"="*30} DATA NORMALIZATION FINISHED')

