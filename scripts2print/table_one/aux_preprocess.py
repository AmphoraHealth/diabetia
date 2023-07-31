# here are the new codes to be used in the transformation or manipulation of the data

import pandas as pd
import os
import sys

# imports from project's root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT_DIR)
from libs import logging

def add_conditions( df:pd.DataFrame):
  """
  Add conditions to the data as new columns:
    - OVERALL: all patients in the database
    - HTN_WO_T2D: patients with hypertension but without type 2 diabetes
    - T2D_WO_HTN: patients with type 2 diabetes but without hypertension
    - TD2_W_HTN: patients with both type 2 diabetes and hypertension
    - NONE: patients with no T2D or HTN
  """

  # add conditions
  df["condition"] = "OVERALL"
  df.loc[(df["diabetes_mellitus_tipo_2"] == 0) & (df["hipertension_esencial_(primaria)"] == 1),"condition"] = "HTN_WO_T2D"
  df.loc[(df["diabetes_mellitus_tipo_2"] == 1) & (df["hipertension_esencial_(primaria)"] == 0),"condition"] = "T2D_WO_HTN"
  df.loc[(df["diabetes_mellitus_tipo_2"] == 1) & (df["hipertension_esencial_(primaria)"] == 1),"condition"] = "T2D_W_HTN"
  df.loc[(df["diabetes_mellitus_tipo_2"] == 0) & (df["hipertension_esencial_(primaria)"] == 0),"condition"] = "NONE"
  
  return df


def add_T2D( df:pd.DataFrame):
  """
  Add T2D diagnosis to the data as a new column.
    - 1: patient has T2D
    - 0: patient does not have T2D
  """

  # get T2D diagnosis
  df["T2D"] = 0
  df.loc[df["diabetes_mellitus_tipo_2"] == 1,"T2D"] = 1

  return df


def add_age_index( df:pd.DataFrame):
  """
  Add age index to the data as a new column.
  """
  df['age_index'] = df['age_at_wx']
  df['age_index_cat'] = pd.cut(
    df['age_index'],
    bins = [0,18,30,40,50,60,70,150],
    right = False,
    labels = ['<18','18-29','30-39','40-49','50-59','60-69','70>']
  )
  return df


def filter_by_window( df:pd.DataFrame, window:int):
  """
  Filter data by window included int he id column.
  the window is the last digit of the id preceded by a -
  """

  # filter by window
  df["_window"] = df["id"].apply(lambda x: int(x.split("-")[-1]))
  df = df[df["_window"] == window]
  df = df.drop(columns=["_window"])

  return df


def preprocess( df:pd.DataFrame, window:int, reduced_sample:bool = False):
  """
  Preprocess the data:
    - add conditions
    - add T2D diagnosis
    - add age index
    - filter by window
  """

  logging.info("Starting data preprocessing")
  df = add_conditions(df)
  df = add_T2D(df)
  df = add_age_index(df)
  df = filter_by_window(df, window)

  if reduced_sample:
    logging.warning("Using reduced sample")
    df = df.sample(frac=0.01, random_state=42)

  return df