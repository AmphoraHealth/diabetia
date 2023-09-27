#!/bin/bash

# This script is used to run the ml-simple.r script

# get the first argument
v0=$1

# print the argument
echo "The first argument is $v0"

# replace the 8th field of v0 with "dummy"
v1=$(echo $v0 | awk -F- '{OFS="-"; $8="dummy"; print}')
echo "The first argument with dummy is $v1"

# replace 07_global_score with 07_conf_int
v2=$(echo $v0 | sed 's/07_global_score/07_conf_int/g'| sed 's/_merged.csv/.txt/g')
echo "The first argument with conf_int is $v2"

# run the R script
echo "Running the R script on $v2"
Rscript scripts4ml/ml-simple.r $v1 $v0 > $v2

# exit with error if the R script fails
if [ $? -ne 0 ]; then
    echo "R script failed"
    exit 1
fi
