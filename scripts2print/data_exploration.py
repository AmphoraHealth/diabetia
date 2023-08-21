# Prepare omop tables from tec's 1500 nursery tables

import json
import os
import sys
from difflib import SequenceMatcher as SM

import pyspark
from pyspark.sql import Window as W
from pyspark.sql import functions as F
import re


# auxiliar functions
def col2table(_dta,_col, v_name, _f = lambda x: x):
  # get initial data
  dta = _dta.select(_col).withColumn(_col,F.udf(_f)(F.col(_col)))

  # group and count
  dta = dta.groupBy(_col).count()

  # column rename
  dta = dta.withColumn("col",F.lit(v_name))

  # percentage estimation
  total = data.count()
  dta = dta.withColumn("perc", F.col("count") / total)

  # return
  return dta.select(["col",_col,"count","perc"]).toPandas().values.tolist()


# Start the pyspark context
spark = pyspark.sql.SparkSession.builder \
    .master("local[10]") \
    .appName(__file__.split(".")[0]) \
    .getOrCreate()
sc = spark.sparkContext

# Start data load
data = spark.read\
    .option("header", "true")\
    .option("delimiter", ",")\
    .option("quote", "\"")\
    .csv(f"data/diabetia.csv",header=True)

# filters to be determined later
data = data.filter(F.col("cx_curp").startswith("AAAA"))

# Table 1 report ------
table1 = [["col","val","missing","frec","porcentage"]]

# Total count of registers
table1.append(["n","","",data.count(),""])

# Distribution by sex
for t in col2table( data, "cs_sexo", "sexo"):
  table1.append(t)


print(table1)
pass