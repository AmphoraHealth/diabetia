""" global_constants.py
    This code is to receive the arguments from the command line and check them.
    The available arguments are:
      - diagnostic
      - origin
      - test_fold
      - balancing_method
      - normalization_method
      - feature_selection_method
      - machine_learning_method
    The argument expected order and valid values is defined in conf/path_constants.json
"""

# Import libraries
import json
import sys
import os

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PATH)

from libs.logging import logging

# constants
_json = json.load(open(f"{ROOT_PATH}/conf/path_constants.json", "r"))
DIAGNOSTICS = _json["diagnostics"]
FOLDS = [str(f) for f in _json["folds"]]
ORIGINS = _json["origins"]
BALANCING_METHODS = _json["balancing_methods"]
NORMALIZATION_METHODS = _json["normalization_methods"]
FEATURE_SELECTION_METHODS = _json["feature_selection_methods"]
MACHINE_LEARNING_MODELS = _json["machine_learning_models"]

# get values from command line
if len(sys.argv) == 1:
  # default values if no argument is given
  logging.warning("no arguments given, using default values")
  DIAGNOSTIC = DIAGNOSTICS[0]
  TEST_FOLD = FOLDS[0]
  ORIGIN = ORIGINS[0]
  BALANCING_METHOD = BALANCING_METHODS[0]
  NORMALIZATION_METHOD = NORMALIZATION_METHODS[0]
  FEATURE_SELECTION_METHOD = FEATURE_SELECTION_METHODS[0]
  MACHINE_LEARNING_MODEL = MACHINE_LEARNING_MODELS[0]
else:
  # get values from command line
  _args = sys.argv[1].split('-')
  # get a list of expected arguments
  _expected_args = _json["_order_in_pipeline"][:len(_args)]
  # sort the list by order in pathname
  _expected_args.sort(key=lambda x: _json["_order_in_pathname"].index(x))
  # auxiliar function to get the value of the argument
  def get_arg_value(arg:str) -> str:
    # Set to None if the argument is not expected
    if not arg in _expected_args:
      return "None"
    # get the position of the argument
    arg_pos = _expected_args.index(arg)
    # get the value of the argument
    arg_val = _args[arg_pos]
    return str(arg_val)
  # set the value of the argument
  DIAGNOSTIC = get_arg_value("diagnostics")
  TEST_FOLD = get_arg_value("folds")
  ORIGIN = get_arg_value("origins")
  BALANCING_METHOD = get_arg_value("balancing_methods")
  NORMALIZATION_METHOD = get_arg_value("normalization_methods")
  FEATURE_SELECTION_METHOD = get_arg_value("feature_selection_methods")
  MACHINE_LEARNING_MODEL = get_arg_value("machine_learning_models")
  
# check values
if not DIAGNOSTIC in DIAGNOSTICS+["None"]:
  raise ValueError(f"given complication ({DIAGNOSTIC}) must be one of {', '.join(DIAGNOSTICS)}")
if not TEST_FOLD in FOLDS+["None"]:
  raise ValueError(f"given test fold ({TEST_FOLD}) must be one of {', '.join(FOLDS)}")
if not ORIGIN in ORIGINS+["None"]:
  raise ValueError(f"given origin ({ORIGIN}) must be one of {', '.join(ORIGINS)}")
if not BALANCING_METHOD in BALANCING_METHODS+["None"]:
  raise ValueError(f"given balancing method ({BALANCING_METHOD}) must be one of {', '.join(BALANCING_METHODS)}")
if not NORMALIZATION_METHOD in NORMALIZATION_METHODS+["None"]:
  raise ValueError(f"given normalization method ({NORMALIZATION_METHOD}) must be one of {', '.join(NORMALIZATION_METHODS)}")
if not FEATURE_SELECTION_METHOD in FEATURE_SELECTION_METHODS+["None"]:
  raise ValueError(f"given feature selection method ({FEATURE_SELECTION_METHOD}) must be one of {', '.join(FEATURE_SELECTION_METHODS)}")
if not MACHINE_LEARNING_MODEL in MACHINE_LEARNING_MODELS+["None"]:
  raise ValueError(f"given machine learning model ({MACHINE_LEARNING_MODEL}) must be one of {', '.join(MACHINE_LEARNING_MODELS)}")

# temporary patch
FS_METHOD = FEATURE_SELECTION_METHOD
ML_MODEL = MACHINE_LEARNING_MODEL

# map keys to values
MAP = {
  "diagnostics": DIAGNOSTIC,
  "folds": TEST_FOLD,
  "origins": ORIGIN,
  "balancing_methods": BALANCING_METHOD,
  "normalization_methods": NORMALIZATION_METHOD,
  "feature_selection_methods": FEATURE_SELECTION_METHOD,
  "machine_learning_models": MACHINE_LEARNING_MODEL,
  "fs_methods": FS_METHOD,
  "ml_models": ML_MODEL
}

# auxiliar function to get the arguments for an specific pipeline step
def _get_args(step:str) -> list:
  # get the mandatory arguments for a pipeline step
  _args = _json["_order_in_pipeline"][:step+1]
  # sort the list by order in pathname
  _args.sort(key=lambda x: _json["_order_in_pathname"].index(x))
  return [MAP[arg] for arg in _args]

# constants for each pipeline step
s00_fold_selection = "data/fold_selection-" + "-".join(_get_args(0))
s01_balancing = "data/balanced-" + "-".join(_get_args(1))
s02_normalization = "data/normalized-" + "-".join(_get_args(2))
s03_feature_selection = "data/features_selected-" + "-".join(_get_args(3))
s04_model_train = "data/model-" + "-".join(_get_args(4))
s05_prediction = "data/prediction-" + "-".join(_get_args(5))
s06_score_by_fold = "data/score-" + "-".join(_get_args(6))
s07_global_score = "data/global_score-" + "-".join(_get_args(7))

# print the values
logging.debug(f"""
  s00_fold_selection: {s00_fold_selection}
  s01_balancing: {s01_balancing}
  s02_normalization: {s02_normalization}
  s03_feature_selection: {s03_feature_selection}
  s04_model_train: {s04_model_train}
  s05_prediction: {s05_prediction}
  s06_score_by_fold: {s06_score_by_fold}
  s07_global_score: {s07_global_score}
""")