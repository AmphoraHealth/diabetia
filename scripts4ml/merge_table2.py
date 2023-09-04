import pandas as pd
from glob import glob

# list output files like data/ml_data/merged_07_global_score-x-*.csv
IN_PATHS = glob(f"data/ml_data/merged_07_global_score-x-*.csv")

# prepare each file
files = [pd.read_csv(IN_PATH) for IN_PATH in IN_PATHS]
for index, df in enumerate(files):
  # keep only code and roc
  df = df[["code", "roc"]]
  # determine the diagnostic from the file name
  diagnostic = IN_PATHS[index].split("-")[2].split(".")[0]
  # rename the roc column to the diagnostic
  df.rename(columns={"roc": diagnostic}, inplace=True)
  # round the roc to 2 decimals
  df[diagnostic] = df[diagnostic].apply(lambda x: round(x, 2))
  # remove the diagnostic from the code
  df["code"] = df["code"].apply(lambda x: x.replace(f"x-{diagnostic}-", ""))
  # replace the file with the new dataframe
  files[index] = df

# join all files
df = files[0]
for file in files[1:]:
  df = df.merge(file, how="outer", on="code")
df.head()

# aux funct
def add_sort(df: pd.DataFrame, pos: int, map: dict):
  # get the unique values in the given position of the code
  values = df["code"].apply(lambda x: x.split("-")[pos]).unique()
  # count initial values in the map
  initial_values = len(map)
  # for each value not in the map, add it to the map
  for value in values:
    if not value in map:
      map[value] = len(map)
  # return the map
  return map, initial_values

# add 0_ord column and fill it with 0
df["0_ord"] = 0

# add 1_ord column
map_pos = 4
map, idx = add_sort(df, map_pos, {
  "dummy": 0
})
df["1_ord"] = df["code"].apply(lambda x: map[x.split("-")[4]])
df.loc[df["1_ord"] >= idx, "0_ord"] = 1

# add 2_ord column
map_pos = 5
map, idx = add_sort(df, map_pos, {
  "logistic": 0,
  "xgboost": 1,
  "gaussian_nb": 2,
  "mlp": 3
})
df["2_ord"] = df["code"].apply(lambda x: map[x.split("-")[5]])
df.loc[df["2_ord"] >= idx, "0_ord"] = 1

# sort rows
df.sort_values(by=["0_ord", "1_ord", "2_ord"], inplace=True)

# get the columns in the correct order
cols = ["code", "e112", "e113", "e114", "e115"]
df = df[cols]

# save the file
df.to_csv("data/ml_data/merged_99_table2.csv", index=False)
pass
