"""
  This code it to encapsulate the saving routines.
  Using function overloading, the function save() can be used to save different types of data.
  The function save() can be used to save:
    - a pandas dataframe (parquet)
    - a dictionary (json)
    - a list (json)
    - an object (pickle)
"""

import pandas as pd
import pickle
import json
import os


def _check_path(_path:str):
  # extract the path of the file
  path = os.path.dirname(_path)
  # create the path if it does not exist
  if not os.path.exists(path):
    os.makedirs(path)


def _check_extension(_path:str, extension:str):
  # check if the extension is in the path
  if not _path.endswith(extension):
    # if not, add it
    _path = f"{_path}.{extension}"
  return _path


def save_data(df:object, path:str):
  if isinstance(df, pd.DataFrame):
    _save_pd(df, path)
  elif isinstance(df, dict):
    _save_dict(df, path)
  elif isinstance(df, list):
    _save_list(df, path)
  else:
    _save_obj(df, path)


def _save_pd(df:pd.DataFrame, path:str):
  _check_path(path)
  df.reset_index(drop=True).to_parquet(_check_extension(path, "parquet"))


def _save_dict(d:dict, path:str):
  _check_path(path)
  with open(_check_extension(path, "json"), "w") as f:
    json.dump(d, f)

def _save_list(l:list, path:str):
  _check_path(path)
  with open(_check_extension(path, "json"), "w") as f:
    json.dump(l, f)

def _save_obj(o:object, path:str):
  _check_path(path)
  with open(_check_extension(path, "pkl"), "wb") as f:
    pickle.dump(o, f)
