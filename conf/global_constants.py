""" global_constants.py
    This code is to receive the arguments from the command line and check them.
    The arguments follow the next order:
      - diagnostic: E112, E113, E114, E115
      - origin: diabetia (unprocessed), discretized
      - test_fold: 0, 1, 2, 3, 4
      - balancing_method: unbalanced, undersampling, oversampling, midsampling
      - normalization_method: zscore, power_transform
      - feature_selection_method: xi2, relieff, probabilistic, mutual_info
      - machine_learning_method: logistic, dt, bernoulli, gaussian
"""

# Import libraries
import sys

# constants
DIAGNOSTICS = ['e112','e113','e114','e115']
ORIGINS = ['diabetia','discretized']
FOLDS = range(5)
BALANCING_METHODS = ['unbalanced','undersampling','oversampling','midsampling']
NORMALIZATION_METHODS = ['zscore','power_transform']
FS_METHODS = ['xi2','relieff','probabilistic','mutual_info']
ML_MODELS = ['logistic','dt','bernoulli','gaussian']

# default values
DIAGNOSTIC = DIAGNOSTICS[0]
ORIGIN = ORIGINS[0]
TEST_FOLD = FOLDS[0]
BALANCING_METHOD = BALANCING_METHODS[0]
NORMALIZATION_METHOD = NORMALIZATION_METHODS[0]
FEATURE_SELECTION_METHOD = FS_METHODS[0]
MACHINE_LEARNING_MODEL = ML_MODELS[0]

# get values from command line
if len(sys.argv) == 1:
  # default values if no argument is given
  print("\n  missing arguments, using default values")
else:
  # get values from command line
  try:
    args = sys.argv[1].split('-')
    DIAGNOSTIC = args[0]
    ORIGIN = args[1]
    TEST_FOLD = int(args[2])
    BALANCING_METHOD = args[3]
    NORMALIZATION_METHOD = args[4]
    FEATURE_SELECTION_METHOD = args[5]
    MACHINE_LEARNING_MODEL = args[6]
  except:
    pass
  
# check values
if not DIAGNOSTIC in DIAGNOSTICS:
  raise ValueError(f"given complication must be one of {', '.join(DIAGNOSTIC)}")
if not ORIGIN in ORIGINS:
  raise ValueError(f"given origin must be one of {', '.join(ORIGIN)}")
if not TEST_FOLD in FOLDS:
  raise ValueError(f"given test fold must be one of {', '.join(TEST_FOLD)}")
if not BALANCING_METHOD in BALANCING_METHODS:
  raise ValueError(f"given balancing method must be one of {', '.join(BALANCING_METHOD)}")
if not NORMALIZATION_METHOD in NORMALIZATION_METHODS:
  raise ValueError(f"given normalization method must be one of {', '.join(NORMALIZATION_METHOD)}")
if not FEATURE_SELECTION_METHOD in FS_METHODS:
  raise ValueError(f"given feature selection method must be one of {', '.join(FS_METHODS)}")
if not MACHINE_LEARNING_MODEL in ML_MODELS:
  raise ValueError(f"given machine learning model must be one of {', '.join(ML_MODELS)}")