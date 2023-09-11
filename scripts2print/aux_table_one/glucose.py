import os
import sys

# Import libraries
import pandas as pd
import numpy as np
import json
import re
import janitor

#..Default configurations
import warnings
warnings.filterwarnings("ignore")

_targetCols:list[str] = [
    "in_glucose_mean",
    "fn_fasting_glucose_mean",
    "fn_capillary_glucose_mean",
    "fn_glycemia_mean"
]

class CreateGlucose:

    def __init__(
            self,
            data:pd.DataFrame,
            col_name:str = None
            ):
        
        assert data.shape[0]>0, 'Dataframe is empty'
        assert all(list(map(lambda x: x in data.columns, _targetCols))), 'Target col not found in index col'

        self.data = data[['id']+_targetCols]
        self.name = 'glucose_value_mean' if col_name == None else col_name

    
    def create(self) -> pd.Series:
        #..default vars
        targetCols:list[str] = _targetCols
        valueColName:str = self.name
        self.data.insert(0,valueColName, self.data[targetCols[0]])

        #..clean glucose under 25
        self.data.loc[
            (self.data[
                self.data[valueColName]<25\
                ]).index,
            valueColName
            ] = np.nan
        
        #..drop 0
        self.data[targetCols] = self.data[targetCols].replace(0,np.nan)

        #..glucose imputation
        self.data.loc[
            (self.data[
                (self.data[valueColName].isnull())\
                & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                ]).index,
            valueColName
            ] = self.data.loc[
                (self.data[
                    (self.data[valueColName].isnull())\
                    & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                    ]).index,
                targetCols[1:]
                ].mean(axis=1)
        
        return self.data[valueColName]


        