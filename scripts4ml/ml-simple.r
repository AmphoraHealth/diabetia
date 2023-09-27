# -----------------------------------------------------------------------------
# R script for AUC and other metrics calculation
# -----------------------------------------------------------------------------
# Script Name: ml-simple.R
# Description: Provides AUC, 95% C.I., BSS, and DeLong
# Author: Arturo Lopez Pineda <arturo [at] amphora.health> + ChatGPT
# Date: Sep 18, 2023
# -----------------------------------------------------------------------------


# Install and load the pROC package (only if not already installed)
print("Installing and loading the pROC package... ---------------------------")
if (!requireNamespace("pROC", quietly = TRUE)) {
  install.packages("pROC", repos = "http://cran.us.r-project.org")
}
library(pROC)
print("Installing and loading the verification package... -------------------")
if (!requireNamespace("verification", quietly = TRUE)) {
  install.packages("verification", repos = "http://cran.us.r-project.org")
}
library(verification)

# print the arguments
print("showing the arguments... ---------------------------------------------")
print(commandArgs(trailingOnly = TRUE))

# 1. Metrics for AUC 1 ----------------------------------------------------
print("Calculating metrics for AUC 1... -------------------------------------")

# Read the CSV file with two columns
# (assuming the file is given as the first argument)
# data <- read.csv("input1.csv")
data <- read.csv(commandArgs(trailingOnly = TRUE)[1])

# Check the structure of the data to ensure it's in the correct format
# If your CSV has headers, you can use header=TRUE in read.csv
# str(data)

# Assuming your CSV file has two columns named 'actual' and 'predicted'
# You can replace these column names with the actual column names in your file
actual_values <- data$actual
predicted_values <- data$predicted


# Calculate the AUC using the roc() function from the pROC package
roc_obj1 <- roc(actual_values, predicted_values)
ci <- ci.auc(roc_obj1, method = "bootstrap", conf.level = 0.95)

# Calculate Brier skill score
brier_skill_score <- verify(actual_values, predicted_values)$ss

# Print the AUC value
cat("AUC:", auc(roc_obj1), "\n")
cat("95% Confidence Interval:", ci[1], "to", ci[2], "\n")
cat("Brier Skill Score:", brier_skill_score, "\n")

# Plot the ROC curve (optional)
plot(roc_obj1, main="ROC Curve")


# 2. Metrics for AUC 2 ----------------------------------------------------
print("Calculating metrics for AUC 2... -------------------------------------")

# Read the CSV file with two columns
# (assuming the file is given as the second argument)
# data <- read.csv("input2.csv")
data <- read.csv(commandArgs(trailingOnly = TRUE)[2])

# Check the structure of the data to ensure it's in the correct format
# If your CSV has headers, you can use header=TRUE in read.csv
# str(data)

# Assuming your CSV file has two columns named 'actual' and 'predicted'
# You can replace these column names with the actual column names in your file
actual_values <- data$actual
predicted_values <- data$predicted


# Calculate the AUC using the roc() function from the pROC package
roc_obj2 <- roc(actual_values, predicted_values)
ci <- ci.auc(roc_obj2, method = "bootstrap", conf.level = 0.95)

# Calculate Brier skill score
brier_skill_score <- verify(actual_values, predicted_values)$ss

# Print the AUC value
cat("AUC:", auc(roc_obj2), "\n")
cat("95% Confidence Interval:", ci[1], "to", ci[2], "\n")
cat("Brier Skill Score:", brier_skill_score, "\n")

# Plot the ROC curve (optional)
plot(roc_obj2, main="ROC Curve")


# 3. Compare two AUCs using DeLong's Method -------------------------------​
print("Comparing two AUCs using DeLong's Method... --------------------------")

# Perform the DeLong test to compare the two ROC curves
delong_test <- roc.test(roc_obj1, roc_obj2, method = "delong")

# Print the results, including p-value and confidence intervals
cat("AUC 1:", auc(roc_obj1), "\n")
cat("AUC 2:", auc(roc_obj2), "\n")
cat("DeLong p-value:", delong_test$p.value, "\n")
cat("95% Confidence Interval for AUC difference:", 
    delong_test$ci[1], "to", delong_test$ci[2], "\n")

# Determine if there is a significant difference
if (delong_test$p.value < 0.001) {
  cat("There is a significant difference between the ROC curves.\n")
} else {
  cat("There is no significant difference between the ROC curves.\n")
}
