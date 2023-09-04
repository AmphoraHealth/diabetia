import pandas as pd

SEED = 42

def undersampling(df:pd.DataFrame, fold_selection:pd.DataFrame, TEST_FOLD:int):
  """
  Undersampling method.
  """
  
  # get all the columns related to diabetes
  cols = [c for c in df.columns if "type_2_diabetes_mellitus" in c]

  # determine which records have or not diabetes (t2dm)
  present = [df[c] != 0 for c in cols]
  present = pd.concat(present, axis=1).any(axis=1)

  # determine which records will or will not have diabetes (t2dm)
  future = df["e11"] != 0

  # list the ids where present and future are true/false
  ids_true = df.loc[present | future, "id"]
  ids_false = df.loc[~present & ~future, "id"]

  # subsample the ids_false to have 1/3 of the original size
  ids_false = ids_false.sample(frac=1/3, random_state=SEED)

  # retrieve the rows in ids_true and ids_false
  df = df.loc[df["id"].isin(ids_true) | df["id"].isin(ids_false)]

  return df