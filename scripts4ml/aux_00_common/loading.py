"""
  This file contains the functions for loading the data.
"""

import pandas as pd
import pickle
import json
import os

def _check_path(_path:str):
  # check if the file exists
  if not os.path.exists(_path):
    raise Exception(f"File {_path} does not exist")

def get_extension(path:str):
  return path.split(".")[-1]


def load_data(path:str):
  _check_path(path)
  extension = get_extension(path)
  if extension == "parquet":
    return _load_parquet(path)
  elif extension == "csv":
    return _load_csv(path)
  elif extension == "json":
    return _load_json(path)
  elif extension == "pkl":
    return _load_pkl(path)
  else:
    raise Exception(f"Extension {extension} not recognized")
  

def _load_parquet(path:str):
  return pd.read_parquet(path)

def _load_csv(path:str):
  return pd.read_csv(path)

def _load_json(path:str):
  return json.load(open(path, "r", encoding="UTF-8"))

def _load_pkl(path:str):
  return pickle.load(open(path, "rb"))
