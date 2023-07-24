import pandas as pd
import numpy as np
import re
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pyinputplus as pyp
from tableone import TableOne
from math import floor,ceil
from scipy.stats import chi2
from itertools import combinations

import warnings
warnings.filterwarnings('ignore')

#..Paths
userInputDataFolder = pyp.inputStr(prompt='FOLDER NAME TO READ FILES: ')
userInputOutputFolder = pyp.inputStr(prompt='FOLDER NAME TO SAVE RESULTS: ')

mainPath = f'/Users/joaquintripp/Documents/GitHub/diabetia/data/ml_data/queries'
outPath = f'/Users/joaquintripp/Documents/GitHub/diabetia/sc-joaquin/hta/ML_database/out/{userInputDataFolder}'
outTable1 = f'/Users/joaquintripp/Documents/GitHub/diabetia/sc-joaquin/hta/ML_database/out/{userInputOutputFolder}'

#..files

tbl_patients = pd.DataFrame()
tbl_consulta = pd.DataFrame()
tbl_diag = pd.DataFrame()
tbl_soma = pd.DataFrame()
tbl_receta = pd.DataFrame()
tbl_diabetes = pd.DataFrame()

def loadData(rows: int=None):
    
    print(f'{"="*30} Loading tables {"="*30}')
    
    global tbl_patients
    global tbl_consulta
    global tbl_diag
    global tbl_soma
    global tbl_receta
    global tbl_diabetes
    
    tbl_patients = pd.read_csv(f'{outPath}/registers.csv', low_memory=False,nrows=rows)
    tbl_consulta = pd.read_csv(f'{mainPath}/ready/corhis_consulta.csv', low_memory=False, nrows=rows)
    tbl_diag = pd.read_csv(f'{mainPath}/ready/exprel_diag.csv', low_memory=False, nrows=rows)
    tbl_soma = pd.read_csv(f'{mainPath}/ready/corhis_somatometria.csv', low_memory=False,nrows=rows)
    tbl_receta = pd.read_csv(f'{mainPath}/ready/receta_med.csv', low_memory=False,nrows=rows)
    tbl_diabetes = pd.read_csv(f'{mainPath}/exphis_diabetes.csv',low_memory=False)
    
    tables = {
        'tbl_patients':tbl_patients.shape,
        'tbl_consulta':tbl_consulta.shape,
        'tbl_diag':tbl_diag.shape,
        'tbl_soma':tbl_soma.shape,
        'tbl_receta':tbl_receta.shape,
        'tbl_diabetes':tbl_diabetes.shape
    }
    
    for k,v in tables.items():
        print(k,v)
        
    return print('Tables has been loaded')


def addPt(tbl_patients:pd.DataFrame):
    pt = tbl_patients[['cx_curp','first_cx','last_cx','df_nacimiento','cs_sexo']].copy().drop_duplicates()
    print(f'Shape after {addPt.__name__}: {pt.shape}')
    return pt



def addAgeIndex(pt:pd.DataFrame):
    #..AGE at index
    pt['age_index'] = (pd.to_datetime(pt['first_cx']) - pd.to_datetime(pt['df_nacimiento'])).dt.days/365
    pt['age_index'] = pt['age_index'].apply(lambda x: floor(x))
    pt['age_index_cat'] = pd.cut(
        pt['age_index'],
        bins = [0,18,30,40,50,60,70,150],
        right = False,
        labels = ['<18','18-29','30-39','40-49','50-59','60-69','70>']
    )
    
    print(f'Shape after {addAgeIndex.__name__}: {pt.shape}')
    return pt


def addAgeDiabetesDxOld(pt:pd.DataFrame, tbl_diabetes:pd.DataFrame):
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
    print(f'Shape after {addAgeDiabetesDx.__name__}: {pt.shape}')
    return pt


def addAgeDiabetesDx(pt:pd.DataFrame, tbl_diabetes:pd.DataFrame, tbl_diag:pd.DataFrame):
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
    
    print(f'Shape after {addAgeDiabetesDx.__name__}: {pt.shape}')
    return pt


def addBMI(pt:pd.DataFrame,tbl_soma:pd.DataFrame):
    """
    For BMI it is requiered to average the last 3 years for each patient. BUT some patients have differences
    between their height measures. In order to save the correct value, the height value is changed by the median
    of the value in the last 3 years. Then BMI is calculated by each consult and finally is averaged. 
    """
    
    #..BMI average
    #....Add Max consult to filter only last 3 years for each patient
    aux_soma = tbl_soma[['cx_curp','df_consulta','year','fn_peso','fn_talla','x_year']].copy()
    aux = aux_soma.groupby(['cx_curp'])['df_consulta'].max().reset_index()
    aux.rename(columns={'df_consulta':'max_consulta'},inplace=True)
    aux_soma = pd.merge(aux_soma,aux,on='cx_curp',how='left')

    #....to datetime
    for n in ['df_consulta','max_consulta']:
        aux_soma[n] = pd.to_datetime(aux_soma[n]).dt.date

    #....years diff vs max consult date
    aux_soma['diff_with_max'] = (aux_soma['max_consulta']-aux_soma['df_consulta']).dt.days / 365
    aux_soma['diff_with_max'] = aux_soma['diff_with_max'].apply(lambda x: ceil(x) if x > 0 else 1)  
    aux_soma['fn_talla'] = aux_soma['fn_talla'].apply(lambda x: np.nan if x<=1 else x)

    #....cleaning fn_talla (median of the last 3 years will be saved)
    """
    Some consults includes kids, the minim age is 6 years old, then a result under 10 in fn_peso
    it is not valid.
    """
    #....add median fn_talla
    aux = aux_soma[(aux_soma['fn_peso']>16.0) & (aux_soma['fn_talla']>1.0) & (aux_soma['diff_with_max']<=3)]\
        .groupby(['cx_curp'])['fn_talla']\
        .median()\
        .reset_index()\
        .rename(columns={'fn_talla':'fn_talla_median'})
    aux_soma = pd.merge(aux_soma,aux,on='cx_curp',how='left')

    #....BMI calculation
    aux_soma['BMI'] = aux_soma['fn_peso']/(aux_soma['fn_talla_median']**2) 

    #....filter of the last 3 years 
    aux_soma = aux_soma[aux_soma['diff_with_max']<=3]
    aux_soma = aux_soma[aux_soma['BMI']>=15]

    #....Median of valid measures
    aux_soma = aux_soma[aux_soma['fn_peso']>16].groupby(['cx_curp'])['BMI'].median().reset_index()
    aux_soma['BMI_cat'] = pd.cut(
        aux_soma['BMI'],
        bins = [0,18.5,25,30,35,40,150],
        right = False,
        labels = ['Underweight','Normal weight','Pre-obesity','Obesity (class 1)','Obesity (class 2)','Obesity (class 3)']
    )
    
    pt = pd.merge(pt,aux_soma,on='cx_curp',how='left')
    print(f'Shape after {addBMI.__name__}: {pt.shape}')
    return pt


def addCieCodes(pt:pd.DataFrame,tbl_diag:pd.DataFrame):
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
    aux_diag['T2D'] = aux_diag[colsDiab].sum(axis=1)
    aux_diag['T2D'] = aux_diag['T2D'].apply(lambda x: 1 if x>0 else 0)
    aux_diag['HTN'] = aux_diag['Hipertensión esencial (primaria)'].apply(lambda x: 1 if x>0 else 0)
    
    #..HTA + Diabetes
    aux_diag['T2D_W_HTN'] = aux_diag['T2D'] + aux_diag['HTN']
    aux_diag['T2D_W_HTN'] = aux_diag['T2D_W_HTN'].apply(lambda x: 1 if x==2 else 0)
    aux_diag = aux_diag.fillna(0)
    
    #..merging auxiliar with conditions to pt
    pt = pd.merge(pt,aux_diag,on='cx_curp',how='left')
    pt[colsCie] = pt[colsCie].fillna(0)
    pt[['T2D','HTN','T2D_W_HTN']] = pt[['T2D','HTN','T2D_W_HTN']].fillna(0)
    
    #..identifying diabetes or hipertension
    pt['condition'] = \
    pt.apply(
        lambda x: 'None' 
            if ((x['T2D'] == 0.0) & (x['HTN'] == 0.0))
            else 'Diabetes'
                if ((x['T2D'] == 1) & (x['HTN'] == 0))
                else 'Hypertension' 
                    if ((x['T2D'] == 0) & (x['HTN'] == 1))
                    else 'Diabetes-Hypertension'
                        if ((x['T2D'] == 1) & (x['HTN'] == 1))
                        else 'Other',
        axis = 1
        )
    
    print(f'Shape after {addCieCodes.__name__}: {pt.shape}')
    return pt


def addCieCodes2(
    pt:pd.DataFrame,
    tbl_diag:pd.DataFrame,
    ):
    """
    This function pivot and add conditions from tbl_diag to pt. Conditions are calculated over all
    period of each patient
    """
    
    #..CIE
    patternDiab = '^E11[0-9]*$'
    patternHta = '^I10.*$'
    patternCancer = '^[C]{1}.*$'
    patternDiabCom = 'E11[2-5]+$'
    
    #..cols
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

    colsDiabCom = \
        list(tbl_diag[
            tbl_diag['catalog_key']\
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
    pt[colsCie] = pt[colsCie].fillna(0)
    pt[['T2D','HTN','T2D_W_HTN','T2D_W_R']] = pt[['T2D','HTN','T2D_W_HTN','T2D_W_R']].fillna(0)
    
    print(f'Shape after {addCieCodes.__name__}: {pt.shape}')
    return pt
    

def imputeCIE(pt:pd.DataFrame):
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
    
    print(f'Shape after {imputeCIE.__name__}: {pt.shape}')
    return pt
    
   
def addCondition(pt:pd.DataFrame):    
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
    
    print(f'Shape after {addCondition.__name__}: {pt.shape}')
    return pt

    

def chi_squared(total1,total2,value1,value2):
    
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
    
def addOR(total1,total2,value1,value2):

    try:
        k11 = int(value1)
        k12 = int(value2)
        k21 = total1-int(value1)
        k22 = total2-int(value2)
        
        odds = (k11/k21)/(k12/k22)
        return odds
    except:
        return np.nan
    

def addCI(total1,total2,value1,value2):
    
    odds = addOR(total1,total2,value1,value2)

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

#..........................
#..Building pt database with categories for table 1
loadData()
pt = addPt(tbl_patients)
pt = addAgeIndex(pt)
pt = addAgeDiabetesDx(pt,tbl_diabetes,tbl_diag)
pt = addBMI(pt,tbl_soma)
pt = addCieCodes2(pt,tbl_diag)
pt = imputeCIE(pt)
pt = addCondition(pt)

if input('Save? [y/n]: ').lower() == 'y':
    
    savePath = '/Users/joaquintripp/delivery/'
    name = str(input('File name: '))
    savePath = savePath+name+'.xlsx'
    pt.to_excel(savePath, encoding='Utf-8',index=False)
    
    if os.path.exists(savePath):
        print('Saved!')
    else:
        print('Error')

#..........................
#..indetifying of cols 
patternDiab = '^E11[0-9]*$'
patternHta = '^I10.*$'
patternCancer = '^[C]{1}.*$'
tbl_dx = tbl_diag[['catalog_key','nombre_tipo','nombre_grupo']].copy().drop_duplicates()


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
        .apply(lambda x: bool(re.match(patternCancer,str(x))))==True]['nombre_grupo']\
        .unique())

colsInfo = [
    'first_cx',
    'last_cx',
    'df_nacimiento',
    'age_index',
    'in_anio_diag',
    'in_anio_diag_cie',
    'anio_dx',
    'age_diag',
    'BMI',
    'Hipertensión esencial (primaria)',
    'condition',
    'cx_curp',
    'T2D',
    'HTN',
    'T2D_W_R',
    'T2D_WH_HTN',
    'T2D_W_HTN',
    'HTN_WH_T2D',
    'imputado',
    'age_index_cat',
    'age_diag_cat'
]

columns = [n for n in pt.columns if n not in colsCancer+colsInfo]
age_columns = ['age_diag','age_index']

#................................
#..Building of table 1

#....Table one groupby condition (OVERALL, HTN_WH_T2D, T2D_WH_HTN, TD2_W_HTN, NONE)
pt_1 = TableOne(
        data = pt, 
        categorical = columns , 
        columns = columns ,
        pval = False, 
        pval_adjust=False, 
        overall = True, 
        label_suffix = True, 
        row_percent = False,
        groupby = 'condition'
)

#....Table one for W_T2D
pt_2 = TableOne(
        data = pt, 
        categorical = columns , 
        columns = columns ,
        pval = False, 
        pval_adjust=False, 
        overall = True, 
        label_suffix = True, 
        row_percent = False,
        groupby = 'T2D'
)

# CONCATENATE OVERALL AND T2D TABLES
"""
For this step, is required to save and read again tables to convert into pandas format.
Both files are concatenated in order to have all groups together
"""
#..DeliveryPath
delyPath = '/Users/joaquintripp/delivery'
out = '/Users/joaquintripp/Documents/GitHub/diabetia/sc-joaquin/hta/ML_database/out'
folder_name = input('Nombre del folder: ')

if not os.path.exists(f'{out}/{folder_name}'):
    os.system(f'mkdir {out}/{folder_name}')
    
pt_1.to_csv(f'{out}/{folder_name}/OVERALL.csv', encoding = 'Utf-8', sep=',')
pt_2.to_csv(f'{out}/{folder_name}/W_T2D.csv', encoding = 'Utf-8', sep=',')

#..Process to overall (OVERALL T2D_WH_HTN, T2D_W_HTN, HTN_WH_T2D,NONE)
pt_ov = pd.read_csv(f'{out}/{folder_name}/OVERALL.csv')
pt_ov.columns = ['Variables','Levels']+[n for n in list(pt_ov.iloc[0:1,:].values[0]) if str(n) != 'nan']

pt_ov = pt_ov[pt_ov['Levels']!='0.0']
pt_ov.drop(pt_ov.iloc[0:1,:].index,inplace=True)
pt_ov.set_index(['Variables','Levels'],inplace=True)

#..Process to W_T2D and WH_T2D
pt_diab = pd.read_csv(f'{out}/{folder_name}/W_T2D.csv')
pt_diab.columns = ['Variables','Levels']+[n for n in list(pt_diab.iloc[0:1,:].values[0]) if str(n) != 'nan']
pt_diab.drop(columns=['Missing','Overall'],inplace=True)
pt_diab.rename(columns = {'0.0':'WH_T2D','1.0':'W_T2D'},inplace=True)

pt_diab = pt_diab[pt_diab['Levels']!='0.0']
pt_diab.drop(pt_diab.iloc[0:1,:].index,inplace=True)
pt_diab.set_index(['Variables','Levels'],inplace=True)

#..CONCATENATE
pt_all = pd.concat([pt_ov,pt_diab],axis=1)

###########################################################################################
"""
pt_all has only diagnosis, sex and BMI categories. With next process Age at index and age
at dx are added.
"""
# AGE INDEX AND AGE DX
#..Age at index
age_1 = pd.concat([
    pt[['age_index']].agg([np.mean,np.median,np.std,'count']).round(2).rename(columns={'age_index':'Overall'}),
    pt.groupby('condition')['age_index'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={'T2D':'T2D_WH_HTN'}),
    pt.groupby('T2D')['age_index'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={0:'WH_T2D',1:'W_T2D'})
],axis=1)[['Overall','W_T2D','T2D_WH_HTN','T2D_W_HTN','WH_T2D']]

age_1 = age_1.set_index([['Age at index']*4,list(age_1.index)])
age_1 = age_1.rename_axis(['Variables','Levels'])

#..Age at diagnosis
age_2 = pd.concat([
    pt[['age_diag']].agg([np.mean,np.median,np.std,'count']).round(2).rename(columns={'age_diag':'Overall'}),
    pt.groupby('condition')['age_diag'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={'T2D':'T2D_WH_HTN'}),
    pt.groupby('T2D')['age_diag'].agg([np.mean,np.median,np.std,'count']).round(2).T.rename(columns={0:'WH_T2D',1:'W_T2D'})
],axis=1)[['Overall','W_T2D','T2D_WH_HTN','T2D_W_HTN','WH_T2D']]

age_2 = age_2.set_index([['Age at Dx']*4,list(age_2.index)])
age_2 = age_2.rename_axis(['Variables','Levels'])

age = pd.concat([age_1,age_2])


# CONCATENATE TABLE ONE
#..Final
ptOne = pd.concat([age,pt_all],axis=0)

#..Order
colsOrder = ['Overall','W_T2D','T2D_WH_HTN','T2D_W_HTN','WH_T2D']
ptOne = ptOne[colsOrder]

#..splitting
for n in colsOrder:
    ptOne[f'({n})'] = ptOne[n].apply(lambda x: float(str(x).split(' ')[0]) if str(x) not in ['None','nan'] else np.nan) 


# CHI2, P-VALUE AND OR
c = combinations(['W_T2D','Overall','T2D_W_HTN','T2D_WH_HTN','WH_T2D'],2)
print(f'{"="*30}Adding CHI2{"="*30}')
for n in c:
    total1 = float(ptOne.loc['n',f'({n[0]})'].values[0]) 
    total2 = float(ptOne.loc['n',f'({n[1]})'].values[0]) 
    colName = f'CHI2 {n[0]}|{n[1]}'
    print(n[0],' vs ',n[1],total1,total2)
    ptOne[colName] = ptOne.iloc[9:,:].apply(lambda x: chi_squared(total1,total2,x[f'({n[0]})'],x[f'({n[1]})']),axis=1).astype(float).round(8)

    
c = combinations(['W_T2D','Overall','T2D_W_HTN','T2D_WH_HTN','WH_T2D'],2)
print(f'{"="*30}Adding OR{"="*30}')
for n in c:
    total1 = float(ptOne.loc['n',f'({n[0]})'].values[0]) 
    total2 = float(ptOne.loc['n',f'({n[1]})'].values[0]) 
    colName = f'OR {n[0]}|{n[1]}'
    print(n[0],' vs ',n[1],total1,total2)
    ptOne[colName] = ptOne.iloc[9:,:].apply(lambda x: addOR(total1,total2,x[f'({n[0]})'],x[f'({n[1]})']),axis=1).astype(float).round(8)


c = [['W_T2D','Overall'],['T2D_W_HTN','W_T2D'],['T2D_W_HTN','T2D_WH_HTN']]
print(f'{"="*30}Adding CI{"="*30}')
for n in c:
    total1 = float(ptOne.loc['n',f'({n[0]})'].values[0]) 
    total2 = float(ptOne.loc['n',f'({n[1]})'].values[0]) 
    colName = f'CI {n[0]}|{n[1]}'
    print(n[0],' vs ',n[1],total1,total2)
    ptOne[colName] = ptOne.iloc[9:,:].apply(lambda x: addCI(total1,total2,x[f'({n[0]})'],x[f'({n[1]})']),axis=1)
 


# SAVING TABLE 1
finalPath = f'{out}/{folder_name}/tbl1.csv'
if os.path.exists(finalPath):
    if input('Overwrite?[y/n]: ').lower() == 'y':
        ptOne.to_csv(finalPath)
        ptOne.to_excel(f'{out}/{folder_name}/tbl1.xlsx')
        print(f'{"="*30} SAVED! {"="*30}')
    else:
        print('Not saved!')
else:
    ptOne.to_csv(finalPath)
    ptOne.to_excel(f'{out}/{folder_name}/tbl1.xlsx')
    print(f'{"="*30} SAVED! {"="*30}')