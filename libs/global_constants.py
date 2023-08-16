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
STANDARDIZATION_METHODS = _json["standardization_methods"]
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
  STANDARDIZATION_METHOD = STANDARDIZATION_METHODS[0]
  FEATURE_SELECTION_METHOD = FEATURE_SELECTION_METHODS[0]
  MACHINE_LEARNING_MODEL = MACHINE_LEARNING_MODELS[0]
else:
  # get values from command line
  _args = sys.argv[1].split('.')[0].split('-')[1:]
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
  STANDARDIZATION_METHOD = get_arg_value("standardization_methods")
  FEATURE_SELECTION_METHOD = get_arg_value("feature_selection_methods")
  MACHINE_LEARNING_MODEL = get_arg_value("machine_learning_models")
  
# report the values
logging.info(f"""
  arguments given:          {sys.argv}
  DIAGNOSTIC:               {DIAGNOSTIC}
  TEST_FOLD:                {TEST_FOLD}
  ORIGIN:                   {ORIGIN}
  BALANCING_METHOD:         {BALANCING_METHOD}
  NORMALIZATION_METHOD:     {NORMALIZATION_METHOD}
  STANDARDIZATION_METHOD:   {STANDARDIZATION_METHOD}
  FEATURE_SELECTION_METHOD: {FEATURE_SELECTION_METHOD}
  MACHINE_LEARNING_MODEL:   {MACHINE_LEARNING_MODEL}
""")
             
# Auxiliar function to determine if the required code is available
def is_available(var:str, code:str, available:list, add_it:bool=False) -> bool:
  logging.info(f"checking if requested {var} is available")
  # if the code is available, return True
  if code in available:
    return True
  # if the code is not available, send a warning and search for his path
  logging.warning(f"code {code} not available, searching for its path")
  dirname = os.path.abspath(os.path.dirname(__file__))\
    .replace(".py", "")\
    .replace("/ml_data/", "/ml_data/aux_")
  file = f"{dirname}/__init__.py"
  # search for the code in the file
  with open(file, "r") as f:
    for line in f.readlines():
      if "import" in line and code in line:
        logging.error(f"code {code} found in {file}\n\tremember to include the code in the file conf/path_constants.json")
        raise ValueError(f"code {code}")
        return True
  # search for the code's file
  file = f"{dirname}/{code}.py"
  if os.path.isfile(file):
    logging.error(f"code {code} found in {file}\n\tremember to include the apropiate line in the file {dirname}/__init__.py")
    raise ValueError(f"code {code}")
  # otherwise, raise an error
  raise ValueError(f"code {code} not found")

is_available("DIAGNOSTIC", DIAGNOSTIC, DIAGNOSTICS+["None"])

# check values
if not DIAGNOSTIC in DIAGNOSTICS+["None"]:
  raise ValueError(f"given complication ({DIAGNOSTIC}) must be one of {', '.join(DIAGNOSTICS)}")
if not TEST_FOLD in FOLDS+["None","x"]:
  raise ValueError(f"given test fold ({TEST_FOLD}) must be one of {', '.join(FOLDS)}")
if not ORIGIN in ORIGINS+["None"]:
  raise ValueError(f"given origin ({ORIGIN}) must be one of {', '.join(ORIGINS)}")
if not BALANCING_METHOD in BALANCING_METHODS+["None"]:
  raise ValueError(f"given balancing method ({BALANCING_METHOD}) must be one of {', '.join(BALANCING_METHODS)}")
if not NORMALIZATION_METHOD in NORMALIZATION_METHODS+["None"]:
  raise ValueError(f"given normalization method ({NORMALIZATION_METHOD}) must be one of {', '.join(NORMALIZATION_METHODS)}")
if not STANDARDIZATION_METHOD in STANDARDIZATION_METHODS+["None"]:
  raise ValueError(f"given standardization method ({STANDARDIZATION_METHOD}) must be one of {', '.join(STANDARDIZATION_METHODS)}")
if not FEATURE_SELECTION_METHOD in FEATURE_SELECTION_METHODS+["None"]:
  raise ValueError(f"given feature selection method ({FEATURE_SELECTION_METHOD}) must be one of {', '.join(FEATURE_SELECTION_METHODS)}")
if not MACHINE_LEARNING_MODEL in MACHINE_LEARNING_MODELS+["None"]:
  raise ValueError(f"given machine learning model ({MACHINE_LEARNING_MODEL}) must be one of {', '.join(MACHINE_LEARNING_MODELS)}")

# temporary patch
FS_METHOD = FEATURE_SELECTION_METHOD
ML_MODEL = MACHINE_LEARNING_MODEL

# map keys to values
MAP = {
  "fake_fold": "x",
  "diagnostics": DIAGNOSTIC,
  "folds": TEST_FOLD,
  "origins": ORIGIN,
  "balancing_methods": BALANCING_METHOD,
  "normalization_methods": NORMALIZATION_METHOD,
  "standardization_methods": STANDARDIZATION_METHOD,
  "feature_selection_methods": FEATURE_SELECTION_METHOD,
  "machine_learning_models": MACHINE_LEARNING_MODEL,
  "fs_methods": FS_METHOD,
  "ml_models": ML_MODEL
}

# auxiliar function to get the arguments for an specific pipeline step
def _get_args(step:str,skip_fold:bool = False) -> list:
  # get the mandatory arguments for a pipeline step
  _args = _json["_order_in_pipeline"][:step+1]
  # sort the list by order in pathname
  _args.sort(key=lambda x: _json["_order_in_pathname"].index(x))
  # remove folds if skip_fold is true
  if skip_fold:
    # if folds is in the list, change it for fake_fold
    if "folds" in _args:
      _args[_args.index("folds")] = "fake_fold"
  return [MAP[arg] for arg in _args]

# constants for each pipeline step
AUX_ORIGIN_DATABASE = "data/diabetia.csv"
S00_FOLD_SPLITING = "data/ml_data/00_folds-" + "-".join(_get_args(0))
AUX_FOLD_SELECTION = "data/ml_data/fold_used-" + "-".join(_get_args(1))
AUX_ORIGIN_SELECTION = "data/ml_data/origin-" + "-".join(_get_args(2))
S01_BALANCING = "data/ml_data/01_balanced-" + "-".join(_get_args(3))
S02A_NORMALIZATION = "data/ml_data/02a_normalized-" + "-".join(_get_args(4))
S02B_STANDARDIZATION = "data/ml_data/02b_scaled-" + "-".join(_get_args(5))
S03_FEATURE_SELECTION = "data/ml_data/03_features-" + "-".join(_get_args(6))
S04_MODEL_TRAIN = "data/ml_data/04_model-" + "-".join(_get_args(7))
S05_PREDICTION = "data/ml_data/05_prediction-" + "-".join(_get_args(8))
S06_SCORE_BY_FOLD = "data/ml_data/06_score-" + "-".join(_get_args(9))
S07_GLOBAL_SCORE = "data/ml_data/07_global_score-" + "-".join(_get_args(10,skip_fold=True))

# print the values
logging.info(f"""
  AUX_ORIGIN_DATABASE:   {AUX_ORIGIN_DATABASE}
  S00_FOLD_SPLITING:     {S00_FOLD_SPLITING}
  AUX_FOLD_SELECTION:    {AUX_FOLD_SELECTION}
  AUX_ORIGIN_SELECTION:  {AUX_ORIGIN_SELECTION}
  S01_BALANCING:         {S01_BALANCING}
  S02A_NORMALIZATION:    {S02A_NORMALIZATION}
  S02B_STANDARDIZATION:  {S02B_STANDARDIZATION}
  S03_FEATURE_SELECTION: {S03_FEATURE_SELECTION}
  S04_MODEL_TRAIN:       {S04_MODEL_TRAIN}
  S05_PREDICTION:        {S05_PREDICTION}
  S06_SCORE_BY_FOLD:     {S06_SCORE_BY_FOLD}
  S07_GLOBAL_SCORE:      {S07_GLOBAL_SCORE}
""")