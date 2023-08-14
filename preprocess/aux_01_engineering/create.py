# Import libraries
import pandas as pd
import numpy as np
import os
import sys
from aux_01_engineering.aux_functions import calculateGFR

ROOT_PATH:str = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        os.path.pardir,
    )
)
sys.path.append(ROOT_PATH)
from libs.logging import logging


class CreateFunctions:
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
            raise logging.error(f'{self.createYearSinceDx.__name__} failed. {e}')
        

    def createAgeDx(self):
        """
        Function to calculate age at T2D diagnosis
        """
        try:
            aux = self.data[['id','birthdate','anio_dx']].sort_values(by=['id','birthdate'], ascending = True)
            aux = aux[aux['anio_dx'].isnull()==False]
            aux = aux.drop_duplicates(subset='id', keep = 'first')
            aux['birthdate'] = pd.to_datetime(aux['birthdate']).dt.year
            aux['age_diag'] = aux['anio_dx'] - aux['birthdate']
            aux_ages:dict = dict(zip(aux['id'],aux['age_diag']))
            self.data.insert(4,'age_diag', self.data['id'].apply(lambda x: aux_ages.get(x,np.nan)))
            return logging.info('Age at Dx created')
        except Exception as e:
            raise logging.error(f'{self.createAgeDx.__name__} failed. {e}')


    def createAgeDxGroup(self):
        """
        Function to stablish categories for Age at T2D diagnosis: 
        18 - 44
        45 - 64
        65 >
        """
        try:
            categories:dict = {
                '18-44':[18,44],
                '45-64':[45,64],
                '65>':[65,120]
            }
            age_diag_index:int = self.data.columns.get_loc('age_diag')
            self.data.insert(age_diag_index+1,'age_diag_cat',np.nan)
            for cat,values in categories.items():
                self.data.loc[
                    (
                        self.data[
                                (self.data['age_diag']>=values[0]) &\
                                (self.data['age_diag']<=values[1])
                            ]
                    ).index,
                    'age_diag_cat'
                    ] = cat

            logging.info(f'Age at T2D Dx group added')

        except Exception as e:
            raise logging.error(f'{self.createAgeDxGroup.__name__} failed. {e}')
        

    def createBmiCategory(self):
        """
        Function to add BMI categories
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']["bmi"]['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']["bmi"]['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['bmi']['targetCols']
            weight:str = targetCols[0]
            height:str = targetCols[1]

            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,'bmi',np.nan)
            self.data.insert(col_index+1,'bmi_label',np.nan)


            self.data.loc[(self.data[(self.data[weight]>0)&(self.data[height]>0)]).index,'bmi'] = \
                self.data.loc[(self.data[(self.data[weight]>0)&(self.data[height]>0)]).index,[weight,height]].apply(lambda x: x[weight] / (x[height]**2), axis=1)

            self.data['bmi_label'] = pd.cut(
                 self.data['bmi'],
                bins = ranges,
                right = False,
                labels = labels
            )

            logging.info('BMI categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createBmiCategory.__name__} failed. {e}')
        

    def createGlucoseCategory(self):
        """
        Function to add glucose categories. There is an imputation for glucose level:
        1. If patient has in_glucose_median = use in_glucose_median
        2. If patient does not have in_glucose_median = use mean of:
            -fn_fasting_glucose_mean,fn_capillary_glucose_mean,fn_glycemia_mean
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']["glucose"]['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']["glucose"]['labels']
            targetCols:list[str] = self.config['categoricalMeasuresConfig']['glucose']['targetCols']
            
            #..Insert new cols in index
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index, 'glucose_index', self.data[targetCols[0]])
            self.data.insert(col_index+1, 'glucose_label', np.nan)

            #..clean glucose under 25
            self.data.loc[
                (self.data[
                    self.data['glucose_index']<25\
                    ]).index,
                'glucose_index'
                ] = np.nan

            #..glucose imputation
            self.data.loc[
                (self.data[
                    (self.data['glucose_index'].isnull())\
                    & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                    ]).index,
                'glucose_index'
                ] = self.data.loc[
                    (self.data[
                        (self.data['glucose_index'].isnull())\
                        & (self.data[targetCols[1:]].isnull().all(axis=1)==False)
                        ]).index,
                    targetCols[1:]
                    ].mean(axis=1)
            
            #..Build label var
            self.data['glucose_label'] = pd.cut(
                self.data['glucose_index'],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Glucose categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createGlucoseCategory.__name__} failed. {e}')
        

    def createHemoglobinCategory(self):
        """
        Function to create hemoglobin categorical col. It is a simple discretization
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['hemoglobin']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['hemoglobin']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['hemoglobin']['targetCols']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,'hemoglobin_index', np.nan)
            self.data.insert(col_index+1,'hemoglobin_label', np.nan)

            #..Build label var
            self.data['hemoglobin_label'] = pd.cut(
                self.data[targetCols[0]],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Hemoglobin categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createHemoglobinCategory.__name__} failed. {e}')
        
    
    def createTriglyceridesCategory(self):
        """
        Function to create triglicerides columns. It is a simple discretization
        """
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['triglycerides']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['triglycerides']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['triglycerides']['targetCols']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,'triglycerides_index', np.nan)
            self.data.insert(col_index+1,'triglycerides_label', np.nan)

            #..Build label var
            self.data['triglycerides_label'] = pd.cut(
                self.data[targetCols[0]],
                bins = ranges,
                labels = labels,
                right = False
                )
            
            logging.info('Triglycerides categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createTriglyceridesCategory.__name__} failed. {e}')
        

    def createDiabeticFootCategory(self):
        try:
            logging.info('Diabetic foot categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createDiabeticFootCategory.__name__} failed. {e}')
        

    def createCreatinineCategory(self):
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['creatinine']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['creatinine']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['creatinine']['targetCols']
            eGFR_Factors:dict = self.config['categoricalMeasuresConfig']['creatinine']['factors']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,'creatinine_index', np.nan)
            self.data.insert(col_index+1,'creatinine_label', np.nan)

            #..apply eGFR
            self.data.loc[
                (self.data[self.data[targetCols[0]].isnull()==False]).index,
                'creatinine_index'
            ] = self.data.loc[
                (self.data[self.data[targetCols[0]].isnull()==False]).index,
                targetCols
            ].apply(
                lambda x: calculateGFR(
                    factors = eGFR_Factors,
                    sex = x[targetCols[2]],
                    age = x[targetCols[1]],
                    creatinine = x[targetCols[0]]
                    ),
                axis = 1
                )
            
            #..Build label var
            self.data['creatinine_label'] = pd.cut(
                self.data['creatinine_index'],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Creatinine categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createCreatinineCategory.__name__} failed. {e}')
        

    def createCholesterolCategory(self):
        try:
            #..default vars
            ranges:list[int] = self.config['categoricalMeasuresConfig']['cholesterol']['ranges']
            labels:list[int] = self.config['categoricalMeasuresConfig']['cholesterol']['labels']
            targetCols:str = self.config['categoricalMeasuresConfig']['cholesterol']['targetCols']

            #..create new cols
            col_index:int = self.data.columns.get_loc(targetCols[0])
            self.data.insert(col_index,'cholesterol_index', np.nan)
            self.data.insert(col_index+1,'cholesterol_label', np.nan)

            #..Build label var
            self.data['cholesterol_label'] = pd.cut(
                self.data[targetCols[0]],
                bins = ranges,
                labels = labels,
                right = False
                )

            logging.info('Cholesterol categorical col created')
        except Exception as e:
            raise logging.error(f'{self.createCholesterolCategory.__name__} failed. {e}')
        

    def __str__(self):
        return 'Data engineering functions'

