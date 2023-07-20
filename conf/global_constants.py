# Import libraries
import sys

# constants
DIAGNOSTIC = ['E112','E113','E114','E115']
METHODS = ['xi2','relieff']
FOLDS = range(5)
MODELS = ['logistic','dt','bernoulli','gaussian']

# default values
DIAGNOSTIC = 'E112'
SELECTION_METHOD = 'xi2'
TEST_FOLD = 0
MODEL = 'logistic'

# get values from command line
if len(sys.argv) == 1:
  # default values if no argument is given
  print("\n  missing argument, using default values")
else:
  # get values from command line
  try:
    args = sys.argv[1].split('-')
    if len(args) >= 1:
      DIAGNOSTIC = args[0]
    if len(args) >= 2:
      SELECTION_METHOD = args[1]
    if len(args) >= 3:
      TEST_FOLD = int(args[2])
    if len(args) >= 4:
      MODEL = args[3]
  except:
    err_l1 = 'given argument must be in the form of {complication}-{method}-{test_fold}-{model}'
    err_l2 = '  not all arguments are required, but they must be in the given order'
    raise ValueError(f"{err_l1}\n{err_l2}")
  
# check values
if not DIAGNOSTIC in DIAGNOSTIC:
  raise ValueError(f"given complication must be one of {', '.join(DIAGNOSTIC)}")
if not SELECTION_METHOD in METHODS:
  raise ValueError(f"given method must be one of {', '.join(METHODS)}")
if not TEST_FOLD in range(5):
  raise ValueError(f"given test fold must be an integer between 0 and {max(FOLDS)}")
if not MODEL in MODELS:
  raise ValueError(f"given model must be one of {', '.join(MODELS)}")