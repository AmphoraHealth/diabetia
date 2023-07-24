import sys

from scipy.stats import chi2
sys.path.append('/Users/joaquintripp/Documents/GitHub/diabetia/sc-joaquin/hta/ML_database')

import pandas as pd
import numpy as np
import re
import os
import json
from datetime import datetime
from datetime import date
from math import ceil
from math import floor

config:dict = json.load(open(f'{os.path.dirname(__file__)}/config.json'))['PATHS']

tbl_patients = pd.DataFrame()
tbl_consulta = pd.DataFrame()
tbl_diag = pd.DataFrame()
tbl_soma = pd.DataFrame()
tbl_receta = pd.DataFrame()
tbl_diabetes = pd.DataFrame()

class Transform:

    def __init__(self):
        pass

    def addPt(self,tbl_patients:pd.DataFrame):
        pt = tbl_patients[['cx_curp','first_cx','last_cx','df_nacimiento','cs_sexo']].copy().drop_duplicates()
        print(f'Shape after {self.addPt.__name__}: {pt.shape}')
        return pt

    def addAgeIndex(self,pt:pd.DataFrame):
        #..AGE at index
        pt['age_index'] = (pd.to_datetime(pt['first_cx']) - pd.to_datetime(pt['df_nacimiento'])).dt.days/365
        pt['age_index'] = pt['age_index'].apply(lambda x: floor(x))
        pt['age_index_cat'] = pd.cut(
            pt['age_index'],
            bins = [0,18,30,40,50,60,70,150],
            right = False,
            labels = ['<18','18-29','30-39','40-49','50-59','60-69','70>']
        )
        
        print(f'Shape after {self.addAgeIndex.__name__}: {pt.shape}')
        return pt


    def addAgeDiabetesDxOld(self,pt:pd.DataFrame, tbl_diabetes:pd.DataFrame):
        #..AGE at dx diabetes
        tbl_diabetes=tbl_diabetes.sort_values(by=['cx_curp','in_anio_diag'],ascending=True).drop_duplicates(subset='cx_curp',keep='first')
        pt = pd.merge(pt,tbl_diabetes, on='cx_curp',how='left')
        pt['age_diag'] = pt['in_anio_diag']-pd.to_datetime(pt['df_nacimiento']).dt.year
        pt['age_diag_cat'] = pd.cut(
            pt['age_diag'],
            bins = [0,18,30,40,50,60,70,150],
            right = False,
            labels = ['<18','18-29','30-39','40-49','50-59','60-69','70>']
        )
        print(f'Shape after {self.addAgeDiabetesDx.__name__}: {pt.shape}')
        return pt


    def addAgeDiabetesDx(self,pt:pd.DataFrame, tbl_diabetes:pd.DataFrame, tbl_diag:pd.DataFrame):
        """
        This function impute diabetes diagnosis date with first dx in tbl_diag. Consult in lucidchart 
        the algorithm. https://lucid.app/lucidchart/3b2d0f7a-ba70-4fef-9f5c-63df5c773f7f/edit?viewport_loc=-167%2C-101%2C2505%2C1075%2C0_0&invitationId=inv_d49bb7b3-82b8-4d63-bfaf-7aff593600d8# 
        """
        
        def findYear(x:pd.DataFrame):
            """
            Function with algorithm
            """ 
            if pd.isnull(x['in_anio_diag']):
                if not pd.isnull(x['in_anio_diag_cie']):
                    year = x['in_anio_diag_cie']
                else:
                    year = np.nan
            else:
                if x['in_anio_diag']==2021:
                    if not pd.isnull(x['in_anio_diag_cie']):
                        year = x['in_anio_diag_cie']
                    else:
                        year = np.nan
                else:
                    year = x['in_anio_diag']

            return year

        #..Census date
        tbl_diabetes = tbl_diabetes.sort_values(by=['cx_curp','in_anio_diag'],ascending=True).drop_duplicates(subset='cx_curp',keep='first')
        pt = pd.merge(pt,tbl_diabetes, on='cx_curp',how='left')
        
        
        #..CIE diagnosis date
        #....patter to filter table
        patternDiab = '^E11[0-9]*$'
        
        #....auxiliar 
        aux = tbl_diag[tbl_diag['catalog_key']\
                .apply(lambda x: bool(re.match(patternDiab,str(x))))==True]\
                .groupby('cx_curp')['df_consulta']\
                .min()\
                .reset_index()
        aux['df_consulta'] = pd.to_datetime(aux['df_consulta']).dt.year
        aux.rename(columns={'df_consulta':'in_anio_diag_cie'},inplace = True)
        
        #..merging col
        pt = pd.merge(pt,aux[['cx_curp','in_anio_diag_cie']], on='cx_curp',how='left')
        
        #..definitive anio diag
        pt['anio_dx'] = pt.apply(lambda x: findYear(x),axis=1)
        
        pt['age_diag'] = pt['anio_dx'] - pd.to_datetime(pt['df_nacimiento']).dt.year
        pt['age_diag_cat'] = pd.cut(
            pt['age_diag'],
            bins = [0,18,30,40,50,60,70,150],
            right = False,
            labels = ['<18','18-29','30-39','40-49','50-59','60-69','70>']
        )
        
        print(f'Shape after {self.addAgeDiabetesDx.__name__}: {pt.shape}')
        return pt


    def addBMI(self,pt:pd.DataFrame,tbl_soma:pd.DataFrame):
        """
        For BMI it is requiered to average the last 3 years for each patient. BUT some patients have differences
        between their height measures. In order to save the correct value, the height value is changed by the median
        of the value in the last 3 years. Then BMI is calculated by each consult and finally is averaged. 
        """
        
        #..BMI average
        aux_soma = tbl_soma[['cx_curp','df_consulta','year','fn_peso','fn_talla','x_year']].copy()
        aux_soma = aux_soma[aux_soma['x_year']>=3]
        aux = aux_soma.groupby(['cx_curp'])['df_consulta'].max().reset_index()
        aux.rename(columns={'df_consulta':'max_consulta'},inplace=True)
        aux_soma = pd.merge(aux_soma,aux,on='cx_curp',how='left')

        for n in ['df_consulta','max_consulta']:
            aux_soma[n] = pd.to_datetime(aux_soma[n]).dt.date

        aux_soma['diff_with_max'] = (aux_soma['max_consulta']-aux_soma['df_consulta']).dt.days / 365
        aux_soma['diff_with_max'] = aux_soma['diff_with_max'].apply(lambda x: ceil(x) if x > 0 else 1)  
        aux = aux_soma\
            .groupby(['cx_curp'])['fn_talla']\
            .median()\
            .reset_index()\
            .rename(columns={'fn_talla':'fn_talla_median'})
        aux_soma = pd.merge(aux_soma,aux,on='cx_curp',how='left')
        aux_soma['BMI'] = aux_soma['fn_peso']/(aux_soma['fn_talla_median']**2)
        aux_soma=aux_soma[aux_soma['diff_with_max']<=3]
        aux_soma = aux_soma.groupby(['cx_curp'])['BMI'].mean().reset_index()
        aux_soma['BMI_cat'] = pd.cut(
            aux_soma['BMI'],
            bins = [0,18.5,25,30,35,40,150],
            right = False,
            labels = ['Underweight','Normal weight','Pre-obesity','Obesity (class 1)','Obesity (class 2)','Obesity (class 3)']
        )
        
        pt = pd.merge(pt,aux_soma,on='cx_curp',how='left')
        print(f'Shape after {self.addBMI.__name__}: {pt.shape}')
        return pt


    def addCieCodes(self,pt:pd.DataFrame,tbl_diag:pd.DataFrame):
        #..CIE
        patternDiab = '^E11[0-9]*$'
        patternHta = '^I10.*$'
        patternCancer = '^[C]{1}.*$'
        
        colsDiab = \
            list(tbl_diag[
                tbl_diag['catalog_key']\
                .apply(lambda x: bool(re.match(patternDiab,str(x))))==True]['nombre_tipo']\
                .unique())

        colsHta = \
            list(tbl_diag[
                tbl_diag['catalog_key']\
                .apply(lambda x: bool(re.match(patternHta,str(x))))==True]['nombre_tipo']\
                .unique())

        colsCancer = \
            list(tbl_diag[
                tbl_diag['catalog_key']\
                .apply(lambda x: bool(re.match(patternCancer,str(x))))==True]['nombre_tipo']\
                .unique())
        
        aux_diag = tbl_diag[['cx_curp','catalog_key','nombre_tipo']].copy().drop_duplicates()
        aux_diag['value'] = 1
        aux_diag = aux_diag[
            (aux_diag['catalog_key'].apply(lambda x: bool(re.match(patternDiab,str(x))))==True)\
            | (aux_diag['catalog_key'].apply(lambda x: bool(re.match(patternHta,str(x))))==True)\
            | (aux_diag['catalog_key'].apply(lambda x: bool(re.match(patternCancer,str(x))))==True)\
        ]
        
        aux_diag = pd.pivot_table(aux_diag,values='value',index='cx_curp',columns='nombre_tipo').reset_index()
        
        #..Diabetes
        aux_diag['Diabetes'] = aux_diag[colsDiab].sum(axis=1)
        aux_diag['Diabetes'] = aux_diag['Diabetes'].apply(lambda x: 1 if x>0 else 0)
        
        #..HTA + Diabetes
        aux_diag['Diabetes_Hipertension'] = aux_diag['Diabetes'] + aux_diag['Hipertensión esencial (primaria)']
        aux_diag['Diabetes_Hipertension'] = aux_diag['Diabetes_Hipertension'].apply(lambda x: 1 if x==2 else 0)
        aux_diag = aux_diag.fillna(0)
        
        #..merging auxiliar with conditions to pt
        pt = pd.merge(pt,aux_diag,on='cx_curp',how='left')
        
        #..identifying diabetes or hipertension
        pt['condition'] = \
        pt.apply(
            lambda x: 'None' 
                if ((x['Diabetes'] == 0.0) & (x['Hipertensión esencial (primaria)'] == 0.0))
                else 'Diabetes'
                    if ((x['Diabetes'] == 1) & (x['Hipertensión esencial (primaria)'] == 0))
                    else 'Hypertension' 
                        if ((x['Diabetes'] == 0) & (x['Hipertensión esencial (primaria)'] == 1))
                        else 'Diabetes-Hypertension'
                            if ((x['Diabetes'] == 1) & (x['Hipertensión esencial (primaria)'] == 1))
                            else 'Other',
            axis = 1
            )
        
        print(f'Shape after {self.addCieCodes.__name__}: {pt.shape}')
        return pt


    def addCieCodes2(self,pt:pd.DataFrame,tbl_diag:pd.DataFrame):
        """
        This function pivot and add conditions from tbl_diag to pt. Conditions are calculated over all
        period of each patient
        """
        #..tbl_diag
        tbl_dx = tbl_diag[['catalog_key','nombre_tipo','nombre_grupo']].copy().drop_duplicates()

        #..CIE
        patternDiab = '^E11[0-9]*$'
        patternHta = '^I10.*$'
        patternCancer = '^[C]{1}.*$'
        patternDiabCom = 'E11[2-5]+$'
        
        #..cols
        colsDiab = \
            list(tbl_dx[
                tbl_dx['catalog_key']\
                .apply(lambda x: bool(re.match(patternDiab,str(x))))==True]['nombre_tipo']\
                .unique())

        colsHta = \
            list(tbl_dx[
                tbl_dx['catalog_key']\
                .apply(lambda x: bool(re.match(patternHta,str(x))))==True]['nombre_tipo']\
                .unique())

        colsCancer = \
            list(tbl_dx[
                tbl_dx['catalog_key']\
                .apply(lambda x: bool(re.match(patternCancer,str(x))))==True]['nombre_tipo']\
                .unique())
        
        colsDiabCom = \
            list(tbl_dx[
                tbl_dx['catalog_key']\
                .apply(lambda x: bool(re.match(patternDiabCom,str(x))))==True]['nombre_tipo']\
                .unique())
        
        #..auxiliar table to pivot conditions by patterns
        aux_diag = tbl_diag[['cx_curp','catalog_key','nombre_tipo','nombre_grupo']].copy().drop_duplicates()
        aux_diag['value'] = 1
        aux_diag = aux_diag[
            (aux_diag['catalog_key'].apply(lambda x: bool(re.match(patternDiab,str(x))))==True)\
            | (aux_diag['catalog_key'].apply(lambda x: bool(re.match(patternHta,str(x))))==True)\
            | (aux_diag['catalog_key'].apply(lambda x: bool(re.match(patternCancer,str(x))))==True)\
        ]
        
        aux_diag['nombre_final'] = aux_diag.apply(lambda x: 
                                                x['nombre_grupo'] 
                                                if bool(re.match(patternCancer,str(x['catalog_key'])))==True
                                                else x['nombre_tipo']
                                                , axis=1
                                                )
        #..Getting cie cols and pivoting table
        colsCie = list(aux_diag['nombre_final'].unique())
        aux_diag = pd.pivot_table(aux_diag,values='value',index='cx_curp',columns='nombre_final').reset_index()
        
        #..Diabetes and hta
        aux_diag['T2D_W_R'] = aux_diag['Diabetes mellitus tipo 2, con complicaciones renales'].apply(lambda x: 1 if x>0 else 0)
        aux_diag['T2D'] = aux_diag[colsDiab].sum(axis=1)
        aux_diag['T2D'] = aux_diag['T2D'].apply(lambda x: 1 if x>0 else 0) 
        aux_diag['HTN'] = aux_diag['Hipertensión esencial (primaria)'].apply(lambda x: 1 if x>0 else 0)
        
        
        #..HTA + Diabetes
        aux_diag['T2D_W_HTN'] = aux_diag['T2D'] + aux_diag['HTN']
        aux_diag['T2D_W_HTN'] = aux_diag['T2D_W_HTN'].apply(lambda x: 1 if x==2 else 0)
        aux_diag = aux_diag.fillna(0)
        
        #..With / without complications (E12-E15)
        aux_diag['Without type 2 Diabetes Mellitus complications'] = aux_diag[colsDiabCom].sum(axis=1).apply(lambda x: 1 if x == 0 else 0)
        aux_diag['With type 2 Diabetes Mellitus complications'] = aux_diag[colsDiabCom].sum(axis=1).apply(lambda x: 1 if x > 0 else 0)
        
        #..mergin pt and filling 0s
        pt = pd.merge(pt,aux_diag,on='cx_curp',how='left')
        pt['Without type 2 Diabetes Mellitus complications'] = pt['Without type 2 Diabetes Mellitus complications'].fillna(1)
        pt['With type 2 Diabetes Mellitus complications'] = pt['With type 2 Diabetes Mellitus complications'].fillna(0)
        pt[colsDiabCom] = pt[colsDiabCom].fillna(0)
        pt[colsCie] = pt[colsCie].fillna(0)
        pt[['T2D','HTN','T2D_W_HTN','T2D_W_R']] = pt[['T2D','HTN','T2D_W_HTN','T2D_W_R']].fillna(0)
        
        print(f'Shape after {self.addCieCodes.__name__}: {pt.shape}')
        return pt


    def imputeCIE(self,pt:pd.DataFrame):
        """
        This function impute CIE code for patients with anio diag but not CIE code
        """
        #..Impute CIE codes with CIE dx dates
        targets = [
        'Diabetes mellitus tipo 2',
        'Diabetes mellitus tipo 2, sin mención de complicación',
        'T2D',
        'imputado'
        ]
        
        pt['imputado'] = 0
        pt[targets] = pt.apply(lambda x: \
                        [1,1,1,1] \
                        if not pd.isnull(x['anio_dx']) and x['T2D'] == 0.0\
                        else x[targets]\
                        , axis = 1\
                        , result_type='expand'\
                        )
        
        #..Validate of new diabetes patients
        pt['T2D_W_HTN'] = pt['T2D'] + pt['HTN']
        pt['T2D_W_HTN'] = pt['T2D_W_HTN'].apply(lambda x: 1 if x==2 else 0)
        
        print(f'Shape after {self.imputeCIE.__name__}: {pt.shape}')
        return pt


    def addCondition(self,pt:pd.DataFrame):    
        """
        This function add the group for each register. 
        """
        
        #..identifying diabetes or hipertension
        pt['condition'] = \
        pt.apply(
            lambda x: 'None' 
                if ((x['T2D'] == 0.0) & (x['HTN'] == 0.0))
                else 'T2D_WH_HTN'
                    if ((x['T2D'] == 1) & (x['HTN'] == 0))
                    else 'HTN_WH_T2D' 
                        if ((x['T2D'] == 0) & (x['HTN'] == 1))
                        else 'T2D_W_HTN'
                            if ((x['T2D'] == 1) & (x['HTN'] == 1))
                            else 'Other',
            axis = 1
        )
        
        print(f'Shape after {self.addCondition.__name__}: {pt.shape}')
        return pt

    def imputeNames(self,pt:pd.DataFrame) -> pd.DataFrame:
        """
        This function: 
        1. Impute column names to return a clean format
        2. Impute sex column
        """
        
        #..defining dictionaries
        columnsReplaces = {
            'T2D_W_R':'Diabetes_renal',
            'T2D':'Diabetes',
            'HTN':'Hipertension',
            'T2D_W_HTN':'Diabetes_Hipertension',
            'With type 2 Diabetes Mellitus complications':'T2D with complications (E112-E115)'
        }
        
        valuesReplaces = {
            'condition':{
                'T2D_W_HTN':'Diabetes-Hipertension',
                'HTN_WH_T2D':'Hipertension',
                'T2D_WH_HTN':'Diabetes'
            },
            'cs_sexo':{
                'M':0,
                'F':1
            }
        }
        
        dropCols = [
            'imputado',
            'Without type 2 Diabetes Mellitus complications'
        ]
        
        #..replacing values
        pt.rename(columns = columnsReplaces,inplace=True)
        pt.replace(to_replace=valuesReplaces, inplace=True)
        pt.drop(columns=dropCols,inplace=True)
        
        print(f'Shape after {self.imputeNames.__name__}: {pt.shape}')
        return pt


    def chi_squared(self,total1,total2,value1,value2):

        try:
            k11 = int(value1)
            k12 = int(value2)
            k21 = total1-int(value1)
            k22 = total2-int(value2)

            rtotal1 = k11+k12
            rtotal2 = k21+k22

            total = total1+total2

            k11p = (total1*rtotal1)/ total
            k12p = (total2*rtotal1)/ total
            k21p = (total1*rtotal2)/ total
            k22p = (total2*rtotal2)/ total

            result = \
                (((k11-k11p)**2)/k11p)\
                + (((k12-k12p)**2)/k12p)\
                + (((k21-k21p)**2)/k21p)\
                + (((k22-k22p)**2)/k22p)



            return chi2.sf(result,1)
        except:
            return np.nan


    def addOR(self,total1,total2,value1,value2):

        try:
            k11 = int(value1)
            k12 = int(value2)
            k21 = total1-int(value1)
            k22 = total2-int(value2)
            
            odds = (k11/k21)/(k12/k22)
            return odds
        except:
            return np.nan

    
    def addCI(self,total1,total2,value1,value2):
    
        odds = self.addOR(total1,total2,value1,value2)

        try:
            k11 = int(value1)
            k12 = int(value2)
            k21 = total1-int(value1)
            k22 = total2-int(value2)
            
            se = np.sqrt((1/k11)+(1/k21)+(1/k12)+(1/k22))
            ci1 = round(np.exp(np.log(odds)-1.96*se),4)
            ci2 = round(np.exp(np.log(odds)+1.96*se),4)
            
            return [ci1,ci2]
        except:
            return np.nan



def run():
    return 


if __name__=='__main__':
    run()

