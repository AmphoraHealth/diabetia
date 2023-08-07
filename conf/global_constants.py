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
  # auxiliar function to get the value of the argument
  def get_arg_value(arg:str) -> str:
    # find the argument position in the list of expected arguments
    arg_pos = _json["_expected_order"].index(arg)
    # get the value of the argument
    if arg_pos < len(_args):
      arg_value = _args[arg_pos]
    else:
      arg_value = "None"
    return str(arg_value)
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
