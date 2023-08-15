# Import libraries
import pandas as pd
import numpy as np
import os
import sys
from sklearn import preprocessing
from aux_01_engineering.aux_functions import snakeCase

ROOT_PATH:str = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging


class CleanFunctions:   
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
            raise logging.error(f'{self.translateColumns.__name__} failed. {e}')
    

    def cleanHeaders(self):
        """
        function to clean headers and json file
        """    
        try:
            #..updating names in file
            self.data.columns = [snakeCase(str(column)) for column in self.data.columns]
            return logging.info('Headers converted into snakeCase')
        except Exception as e:
            raise logging.error(f'{self.cleanHeaders.__name__} failed. {e}')


    def cleanCareunit(self):
        """
        Function to clean careunit and transform it into onehot
        """
        try:
            #....one hot for cd_hallazgo
            auxOneHot: pd.DataFrame = pd.get_dummies(self.data['careunit'])
            auxOneHot.columns = [ snakeCase(col) for col in auxOneHot.columns]
            careunit_index:int = self.data.columns.get_loc('careunit')
            self.data.drop(columns=['careunit'],inplace=True)

            #..sort cols
            for idx, col in enumerate(auxOneHot.columns):
                self.data.insert(careunit_index + idx, col, auxOneHot[col])

            logging.info(f'Careunit transformed into oneHot')
        except Exception as e:
            raise logging.error(f'{self.cleanCareunit.__name__} failed. {e}')


    def categoricalCols(self):
        """
        Function to clean categorical columns. It is required to write in engineering_conf
        the columns which are consider as categorical. For this columns will be transformed into
        labels with LabelEnconder from sklearn. There are two types of clean:
        1. Clean categorical with non ordinal labels
        2. Clean categorical with ordinal labels
        """
        try:
            #..Get categorical cols from json config and encoder from sklearn
            categoricalCols:list[str] = self.config['config']['categorical_cols']
            label_encoder:object = preprocessing.LabelEncoder()
            
            ######################### Categorical non ordinal
            for col in categoricalCols:
                self.data[col] = label_encoder.fit_transform(self.data[col])

            ######################### Categorical ordinal
            for measure in self.config['categoricalMeasuresConfig'].items():
                labels:list[str] = measure[1]['labels']

                if measure[0] == 'creatinine':
                    labels = labels[::-1]

                categories:dict = {
                    category:index for index, category in enumerate(labels)
                }

                #..inserting new col
                col_index:int = self.data.columns.get_loc(measure[1]['labelCol'])
                self.data.insert(col_index+1,measure[1]['ordinalCol'],np.nan)
                self.data[measure[1]['ordinalCol']] = self.data[measure[1]['labelCol']].map(categories)
                
                
            return logging.info('Categorical cols transformed')
        
        except Exception as e:
            raise logging.error(f'{self.categoricalCols.__name__} failed. {e}')
        

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
            raise logging.error(f'{self.ordinalCols.__name__} failed. {e}') 
