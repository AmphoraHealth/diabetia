import pandas as pd

def unbalanced(df:pd.DataFrame, fold_selection:pd.DataFrame, TEST_FOLD:int):
  """
  No balancing method.
  Retuns all the data not in the test fold.
  """
  
  return df