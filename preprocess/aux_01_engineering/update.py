# Import libraries
import pandas as pd
import os
import sys
import json
from alive_progress import alive_bar

ROOT_PATH:str = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
    )
)
COLUMNS_JSON_PATH:str = f'{ROOT_PATH}/conf/columnGroups.json'
sys.path.append(ROOT_PATH)
from libs.logging import logging

class UpdateFunctions:
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
            raise logging.error(f'Y Values were not transformed. {e}')
        

    def updateJsonCols(self):
        """
        Function to update json file with col names by group
        """
        try:
            initial_demograhics:int = self.data.columns.get_loc('id')
            initial_diagnosis:int = self.data.columns.get_loc('diabetes_mellitus_type_2')
            initial_measures:int = self.data.columns.get_loc('fn_weight_mean')
            initial_drugs:int = self.data.columns.get_loc('antivertigious_sum')
            initial_predictions:int = self.data.columns.get_loc('e11')

            #..Columns list by group
            demographicsCols:list[str] = list(self.data.columns[:initial_diagnosis])
            diagnosisCols:list[str] = list(self.data.columns[initial_diagnosis:initial_measures])
            measuresCols:list[str] = list(self.data.columns[initial_measures:initial_drugs])
            drugsCols:list[str] = list(self.data.columns[initial_drugs:initial_predictions])
            predictionsCols:list[str] = list(self.data.columns[initial_predictions:])

            columns:dict = dict({
                "demographicCols":demographicsCols,
                "diagnosisCols":diagnosisCols,
                "measuresCols":measuresCols,
                "drugsCols":drugsCols,
                "predictionCols":predictionsCols
            })

            with open(COLUMNS_JSON_PATH, 'w', encoding='UTF-8') as outfile:
                json.dump(columns, outfile, indent=4, ensure_ascii=False)

            totalCols:int = \
                len(demographicsCols)\
                +len(diagnosisCols)\
                +len(measuresCols)\
                +len(drugsCols)\
                +len(predictionsCols)
            
            assert totalCols != self.data.shape[0], 'Columns saved are different from data.columns'

            logging.info(f'columnGroups.json saved in ./config. {totalCols} columns.')
        except Exception as e:
            raise logging.error(f'{self.updateJsonCols.__name__} failed. {e}')

    
    def updatePredictions(self):
        """
        Function to update predictions. E11 is to indicate if patient has or not T2D in window. From origin, those prediction
        cols come from original diagnosis, then in some cases, physician do not registered E11, he registered E119. But some other cases
        only a complication was registered as E11.2 and E11 was not mapped. 
        """
        try:
            #..requeried variables
            initial_predictions:int = self.data.columns.get_loc('e11')
            yxCols:list[str] = list(self.data.columns[initial_predictions:])

            #..clen of e11
            self.data.loc[(self.data[self.data[yxCols].sum(axis=1)>0]).index, 'e11'] = 1
            return logging.info(f'E11 diagnosis was cleaned')
        except Exception as e:
            raise logging.error(f'{self.updatePredictions.__name__} failed. {e}')
