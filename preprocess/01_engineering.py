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
IN_PATH = './data/hk_database.csv'
OUT_PATH = './data/hk_database_cleaned.csv'
CONFIG_PATH = './conf/engineering_conf.json'

# Import libraries
import pandas as pd
import numpy as np
import re
import os
import logging
import json
import sys
from sklearn import preprocessing
from alive_progress import alive_bar

#..Default configurations
logging_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=logging_format, datefmt='%d-%m-%y %H:%M:%S')

#############################################################################
# Auxiliar functions
#############################################################################

def snakeCase(string:str) -> str:
    """
    Function to change a string into snake case
    """
    string = str(string)
    replaces = {
        'á':'a',
        'é':'e',
        'í':'i',
        'ó':'o',
        'ú':'u',
        'ñ':'n',
        ' ':'_',
        ',':'',
        '.':'',
        '[':'',
        ']':'',
        '-':'_'
    }
    
    string = string.split()
    string = [s.strip().lower() for s in string]
    string = '_'.join(string)
        
    for k,v in replaces.items():
        string = string.replace(k,v)
    
    return string

 #############################################################################   

class DataEngineering:
    
    def __init__(
        self,
        IN_PATH:str,
        CONFIG_PATH:str
      ):
        self.in_path:str = IN_PATH
        self.config_path:str = CONFIG_PATH
        self.data:pd.DataFrame = pd.DataFrame()
        self.config:dict = json.load(open(f'{self.config_path}', 'r'))


    def mainTransform(self) -> pd.DataFrame:
        """
        Function to run all transformations.
        """
        try:
            #..Transformations starts
            self.readFile()
            self.translateColumns()
            self.cleanHeaders()
            self.createAgeDx()
            self.createYearSinceDx()
            self.categoricalCols()
            self.ordinalCols()
            self.updateDiagnosis()
            self.dropCols()

            logging.info('Transformations done')
            return self.data
        except Exception as e:
            return logging.warning(f'Transformations failed. {e}')
    

    def readFile(self,rows:int = None):
        try:
            self.data = pd.read_csv(f'{self.in_path}', low_memory=False, nrows=rows)
            return logging.info('File read')
        except Exception as e:
            return logging.warning(f'File was not read. {e}')
          
    
    def translateColumns(self):
        """
        Function to translate spanish Columns into english. To consult this translation go to config.json file
        """
        try:
            #..translation dictionary
            translation:dict = self.config['columnNamesTranslation']
            self.data.columns = [translation.get(name,'error') for name in self.data.columns]
            logging.info(f'Columns translated into english')
        except Exception as e:
            logging.warning(f'{self.translateColumns.__name__} failed. {e}')


    def cleanHeaders(self):
        """
        function to clean headers and json file
        """    
        try:
            #..updating names in file
            self.data.columns = [snakeCase(str(column)) for column in self.data.columns]
            return logging.info('Headers converted into snakeCase')
        except Exception as e:
            logging.warning(f'{self.cleanHeaders.__name__} failed. {e}')


    def dropCols(self):
        """
        Function to drop next columns:
        - unnecesary columns or informative
        - empty columns
        - all columns that are counts
        - drop std (pending)
        """   
        try:
            #..Drop unncessesary columns by json file
            dropUnnecessaryCols:list[str] = self.config['config']['columnsToDrop']['unnecessaryCols']
            self.data.drop(columns=dropUnnecessaryCols, inplace=True)

            #..Drop empty columns
            dropEmptyCols:list[str] = self.data.columns[self.data.isnull().all()]
            self.data.drop(columns=dropEmptyCols, inplace=True)

            #..Drop counts
            dropCountColumns:list[str] = [n for n in self.data.columns if bool(re.match('^.*count$',n)) == True]
            self.data.drop(columns=dropCountColumns, inplace=True)

            columnsDropped:int = len(dropUnnecessaryCols)\
                +len(dropEmptyCols)\
                +len(dropCountColumns)
            
            return logging.info(f'{columnsDropped} columns dropped')
        
        except Exception as e:
            return logging.warning(f'Columns were not dropped. {e}')
        

    def categoricalCols(self):
        """
        Function to clean categorical columns. It is required to write in engineering_conf
        the columns which are consider as categorical. For this columns will be transformed into
        labels with LabelEnconder from sklearn.
        """
        try:
            #..Get categorical cols from json config and encoder from sklearn
            categoricalCols:list[str] = self.config['config']['categorical_cols']
            encoder:object = preprocessing.LabelEncoder()
            
            #..Loop all columns in config
            for col in self.config['config']['categorical_cols']:
                self.data[col] = encoder.fit_transform(self.data[col])
                
            return logging.info('Categorical cols transformed')
        
        except Exception as e:
            return logging.warning(f'{self.categoricalCols.__name__} failed. {e}')
        

    def ordinalCols(self):
        """
        Function to clean ordinal columns. It is required to write in engineering_conf
        the columns which are consider as ordinal. 
        """
        try:
            #..Get ordinal cols from json config file
            ordinalCols:list[str] = self.config['config']['ordinal_cols']

            #..Loop all columns in config
            for column in ordinalCols:
                self.data[column] = \
                    pd.to_datetime(self.data[column], errors='coerce')\
                    .apply(lambda x: x.toordinal() if pd.isnull(x) == False else x)
                
            return logging.info('Ordinal cols transformed')
        except Exception as e:
            return logging.warning(f'{self.ordinalCols.__name__} failed. {e}') 
    

    def updateDiagnosis(self): 
        """
        Function to change the Y variables into multilabel vars depending on the case it represents
        (Y vars are include also in X vars). 
        The cases are classified as follow:
        Considering [X,Y]:
        1. [0,0] = 0
        2. [0,1] = 1
        3. [1,1] = 2
        """  
        try:
            #..Get diagnosis columns from json config file
            dxCols:dict[str:str] = self.config['config']['diagnosis']

            #..Loop through dxCols dictionary to clean each dx
            with alive_bar(len(dxCols.keys()), title='### Y Values in transformation') as bar:
                for cie, name in dxCols.items():
                    self.data.loc[(self.data[(self.data[name] == 0) & (self.data[cie]==0)]).index,cie] = 0
                    self.data.loc[(self.data[(self.data[name] == 0) & (self.data[cie]==1)]).index,cie] = 1
                    self.data.loc[(self.data[(self.data[name] == 1) & (self.data[cie]==1)]).index,cie] = 2
                    bar()
            return logging.info(f'Y Values transformed into labels')
        except Exception as e:
            return logging.warning(f'Y Values were not transformed. {e}')
        
    
    def createYearSinceDx(self):
        """
        Function to update anio_dx for year since T2D diagnosis
        """
        try:
            yearsSinceDx = pd.to_datetime(self.data['x_start']).dt.year
            self.data.insert(3,'years_since_dx', yearsSinceDx)
            self.data['years_since_dx'] = self.data.apply(lambda x: x['years_since_dx']-x['anio_dx'] if x['anio_dx'] > 0  else 0,axis=1)
            self.data.loc[(self.data[self.data['years_since_dx']<0]).index,'years_since_dx'] = 0
            return logging.info('Year since Dx updated')
        except Exception as e:
            return logging.warning(f'{self.createYearSinceDx.__name__} failed. {e}')
        
    
    def createAgeDx(self):
        """
        Function to calculate age at T2D diagnosis
        """
        try:
            aux = self.data[['id','df_nacimiento','anio_dx']].sort_values(by=['id','df_nacimiento'], ascending = True)
            aux = aux[aux['anio_dx'].isnull()==False]
            aux = aux.drop_duplicates(subset='id', keep = 'first')
            aux['df_nacimiento'] = pd.to_datetime(aux['df_nacimiento']).dt.year
            aux['age_diag'] = aux['anio_dx'] - aux['df_nacimiento']
            aux_ages:dict = dict(zip(aux['id'],aux['age_diag']))
            self.data.insert(4,'age_diag', self.data['id'].apply(lambda x: aux_ages.get(x,np.nan)))
            return logging.info('Age at Dx created')
        except Exception as e:
            return logging.warning(f'{self.createAgeDx.__name__} failed. {e}')

    def __str__(self):
        return 'Data engineering transformations'


def runDataEngineering() -> pd.DataFrame:
    """
    Function to run all data engineering process
    """
    # intialize class
    try:
      data_engineering = DataEngineering(
          IN_PATH=IN_PATH,
          CONFIG_PATH=CONFIG_PATH
      )

      # Run transformations
      data = data_engineering.mainTransform()

      # Save file
      data.to_csv(f'{OUT_PATH}', index=False, encoding='UTF-8')
      
      return logging.info(f'File saved on {OUT_PATH}')
    
    except Exception as e:
        return logging.warning(f'{runDataEngineering.__name__} process failed. {e}')


if __name__ == '__main__':
    logging.info(f'{"="*30}DATA ENGINEERING STARTS')
    runDataEngineering()
    logging.info(f'{"="*30}DATA ENGINEERING FINISHED')