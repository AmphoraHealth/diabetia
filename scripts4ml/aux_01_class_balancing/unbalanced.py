import pandas as pd

def unbalanced(df:pd.DataFrame, fold_selection:pd.DataFrame, TEST_FOLD:int):
  """
  No balancing method.
  Retuns all the data not in the test fold.
  """
  # get the list of valid ids not in the test fold
  folds = [fold_selection[str(i)]["ids"] for i in range(5) if str(i) != TEST_FOLD]
  ids = [item for sublist in folds for item in sublist]

  # filter the data to get only rows where the id is in the list
  df = df.loc[df["id"].isin(ids)]
  return df