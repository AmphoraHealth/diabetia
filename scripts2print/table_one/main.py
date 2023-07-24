import sys
sys.path.append('/Users/joaquintripp/Documents/GitHub/diabetia/sc-joaquin/hta/ML_database')

import pandas as pd
import numpy as np
import re
import os
import pyinputplus as pyp
import json
from table_one import *
from math import ceil
from math import floor

CONFIG:dict = json.load(open(f'{os.path.dirname(__file__)}/config.json'))['PATHS']

def run():

    #..reading tables
    userInputDataFolder = pyp.inputStr(prompt='FOLDER NAME TO READ FILES: ')
    userInputOutputFolder = pyp.inputStr(prompt='FOLDER NAME TO SAVE RESULTS: ')

    read = Read(folder=userInputDataFolder, outFolder=userInputDataFolder)
    tables = read.run()
    globals().update(**tables)
    """
    The previous line returns in global variables next tables: tbl_patients, tbl_consulta,
    tbl_diag, tbl_soma, tbl_receta and tbl_diabetes
    """
    del tables

    #..........................
    #..Building pt database with categories for table 1
    transform = Transform()
    pt = transform.addPt(tbl_patients)
    pt = transform.addAgeIndex(pt)
    pt = transform.addAgeDiabetesDx(pt,tbl_diabetes,tbl_diag)
    pt = transform.addBMI(pt,tbl_soma)
    pt = transform.addCieCodes2(pt,tbl_diag)
    pt = transform.imputeCIE(pt)
    pt = transform.addCondition(pt)
    if input('Input names? [y/n]: ').lower() == 'y':
        pt = transform.imputeNames(pt)

    if input('Save? [y/n]: ').lower() == 'y':
        
        name = str(input('File name: '))
        savePath = f'{CONFIG["outPath"]}/{userInputDataFolder}/{name}.xlsx'
        pt.to_excel(savePath, encoding='Utf-8',index=False)
        pt.to_csv(savePath,index=False)
        
        if os.path.exists(savePath):
            print('Saved!')
        else:
            print('Error')


    return



if __name__ == '__main__':
    run()
    