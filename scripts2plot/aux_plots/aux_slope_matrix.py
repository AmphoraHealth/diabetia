"""
slope_plot.py
This file contains the main function to create a database with slopes by variable. All numerical variables 
are considering for heatmap but to slope plot only a slice of them are consider. 

Input:
  - data/diabetia.csv
Output:
  class object
"""

# Constants
IN_PATH = './data/diabetia.csv'
CONFIG_PATH = './conf/engineering_conf.json'

# Import libraries
import pandas as pd
import numpy as np
import re
import os
import json
import sys
from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from alive_progress import alive_bar

ROOT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir
    )
)

sys.path.append(ROOT_PATH)
from libs.logging import logging


#..it is required to have a dictionary with {'name':'query'} by filter from Dashhealth
#..This is an example of desireble filters dictionary. It can be as long as user add groups in filters
class SlopeDatabaseConstructor:


    def __init__(
            self,
            data:pd.DataFrame,
            columns:dict[str:str],
            groups:list[str],
            config_path:str = CONFIG_PATH
    ):
        self.data = data
        self.columns = columns
        self.groups = groups
        self.config_path = CONFIG_PATH


    def fit_transform(self):
        """
        Function to transform data from diabetia.csv into a new dataframe. It is required to give a 
        columns dictionary as an input, with original name as key and a formatted name as item. The data
        is grouped by:
            - T2D Complication group
                0: 0-0
                1: 0-1
                2: 0-2
            - measure
        And columns are:
            - windows
        After slope and b are added to the dataframe. This new dataframe is ready to plot 
        into a heatmap or lineplot with slopes.
        """
        return self._transform()


    def _calculateSlope(
            self,
            y_values:list[float]
        ) -> float:
        """
        Function to calcualte m for a list of values. 
        """

        try: 
            # x and y parameters 
            x  = np.arange(1,len(y_values)+1).reshape(-1,1)
            y = np.array(y_values).reshape(-1,1)

            # drop nulls
            x = np.array([x for x,y in zip(x,y) if pd.isnull(y)==False]).reshape(-1,1)
            y = np.array([y for y in y if pd.isnull(y)==False]).reshape(-1,1)

            # do simple linear regression to calculate coefs
            regression = LinearRegression()
            regression = regression.fit(x,y)
            m = regression.coef_[0][0]
            b = regression.intercept_[0]

            return m,b
        
        except Exception as e: 
            logging.warning(e)

            return np.nan,np.nan
        
    def _transform(self) -> pd.DataFrame:
        """
        Function to transform and give 
        """
        try:
            #..validate self.groups list
            assert len(self.groups)>0, 'Categories to group by are missing'

            #..initialize final df
            data:pd.DataFrame = pd.DataFrame()

            #..do category by category
            for category in self.groups:
                new_data = self._summarize(group = category)
                data = pd.concat(
                    [data, new_data],
                    axis=0,
                    ignore_index = True
                )
            data.reset_index(drop=True, inplace=True)
        
            #..replace categories for string values
            data.replace(
                to_replace={
                    'categories':{
                        0.0:'No complications',
                        1.0:'Novo complications',
                        2.0:'Existing complications'
                    }
                },
                inplace = True
            )
            return data

        except Exception as e:
            raise logging.error(f'{self._transform.__name__} failed. {e}')
        
    def _summarize(self, group:str) -> pd.DataFrame:
        """
        Function to preprocess data from diabetia.csv
        """
        
        try:
            #..set a copy of data
            data = self.data.copy()

            #..split id and window
            data.insert(0,'p_id',data['id'].apply(lambda x: x.split('-')[0]))
            data.insert(0,'window',data['id'].apply(lambda x: x.split('-')[1]))
            data['window'] = data['window'].astype('int64')

            #..filter columns required
            data = (
                data[
                    ['window',group]\
                    +list(self.columns.keys())
                ]
                .rename(columns={group:'categories'})
                )
            data.insert(1,'group_name',group)
        
            #..Get new dataframe with data summarized by age label, measure and columns are now windows
            data[[col for col in data.columns if col != 'categories']] = data[[col for col in data.columns if col != 'categories']].replace(0,np.nan)
            data = pd.melt(data,id_vars=['group_name','categories','window'])
            data = pd.pivot_table(
                data,
                index = ['group_name','categories','variable'],
                columns = 'window',
                aggfunc = 'mean'
                ).reset_index()
            data.columns = ['group_name','categories','concept_name']+[col[1] for col in data.columns if col[1]!='']
            data[[col for col in data.columns if col != 'categories']] = data[[col for col in data.columns if col != 'categories']].replace(0,np.nan)

            #..calculate slope
            if 15 in data.columns:
                data.drop(columns = 15, inplace=True)
            data[['m','b']] = data.iloc[:,3:].apply(lambda x: self._calculateSlope(list(x)),axis=1, result_type='expand')
            
            logging.info(f'Data transformed for group: {group}')
            return data
        except Exception as e:
            raise logging.error(f'{self._summarize.__name__} failed. {e}')