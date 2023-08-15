# short names:
create_env: .venv/bin/activate

diabetia: data/diabetia.csv

download: data/hk_database.csv

clean:
	rm -rf data/ml_data/0*
	rm -rf data/ml_data/fold_used-*
	rm -rf data/ml_data/prebalanced-*

test: data/ml_data/06_score-0-e112-diabetia-unbalanced-yeo_johnson-z_score-xi2-knc.csv

clean-test: clean test

# initial setup
.venv/bin/activate: bash/run_enviroment.sh requirements.txt
	bash bash/run_enviroment.sh

data/hk_database.csv:
	cd data && make hk_database.csv
	@echo "Downloaded hk_database.csv"

# Special targets
.PRECIOUS: data/diabetia.csv data/hk_database.csv data/ml_data/00_folds-%.json data/ml_data/fold_used-% data/ml_data/01_balanced-%.csv data/ml_data/02a_normalized-%.csv data/ml_data/03_features-%.json data/ml_data/04_model-%.pkl data/ml_data/05_prediction-%.csv
.INTERMEDIATE: data/hk_database_cleaned.csv

# preprocess data
data/hk_database_cleaned.csv: data/hk_database.csv preprocess/01_engineering.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/01_engineering.py

data/diabetia.csv: data/hk_database_cleaned.csv preprocess/02_imputation.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/02_imputation.py

data/ml_data/00_folds-%.json: data/diabetia.csv preprocess/03_fold_selection.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/03_fold_selection.py $@
	test -f $@

# Machine learning
ph/fold_used-0-% ph/fold_used-1-% ph/fold_used-2-% ph/fold_used-3-% ph/fold_used-4-%: data/ml_data/00_folds-%.json
	@echo "phony target $@"
data/ml_data/fold_used-%: ph/fold_used-%
	@rm $@ || true
	touch $@

ph/prebalanced-%-diabetia: data/ml_data/fold_used-% ph/fold_used-%
	@echo "phony target $@"
data/ml_data/prebalanced-%: data/diabetia.csv ph/prebalanced-% .venv/bin/activate
	@unlink $@ || true
	ln -s data/diabetia.csv $@

ph/01_balanced-%-unbalanced: data/ml_data/prebalanced-% ph/prebalanced-% scripts4ml/aux_01_class_balancing/unbalanced.py
	@echo "phony target $@"
ph/01_balanced-%-oversampling: data/ml_data/prebalanced-% ph/prebalanced-% scripts4ml/aux_01_class_balancing/oversampling.py
	@echo "phony target $@"
ph/01_balanced-%-undersampling: data/ml_data/prebalanced-% ph/prebalanced-% scripts4ml/aux_01_class_balancing/undersampling.py
	@echo "phony target $@"
ph/01_balanced-%-mixed: data/ml_data/prebalanced-% ph/prebalanced-% scripts4ml/aux_01_class_balancing/mixed.py
	@echo "phony target $@"
data/ml_data/01_balanced-%.csv: ph/01_balanced-% scripts4ml/01_class_balancing.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/01_class_balancing.py $@
	test -f $@

ph/02a_normalized-%-yeo_johnson: data/ml_data/01_balanced-%.csv ph/01_balanced-% scripts4ml/aux_02a_data_normalization/yeo_johnson.py
	@echo "phony target $@"
ph/02a_normalized-%-box_cox: data/ml_data/01_balanced-%.csv ph/01_balanced-% scripts4ml/aux_02a_data_normalization/box_cox.py
	@echo "phony target $@"
ph/02a_normalized-%-quantile_transform: data/ml_data/01_balanced-%.csv ph/01_balanced-% scripts4ml/aux_02a_data_normalization/quantile_transform.py
	@echo "phony target $@"
data/ml_data/02a_normalized-%.csv: ph/02a_normalized-% scripts4ml/02a_data_normalization.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/02a_data_normalization.py $@
	ls data/ml_data/
	echo $@ | sed 's/\.csv/\.pkl/' | xargs test -f
	echo $@ | sed 's/\.csv/\.json/' | xargs test -f
	test -f $@

ph/02b_scaled-%-z_score: data/ml_data/02a_normalized-%.csv ph/02a_normalized-% scripts4ml/aux_02b_data_standardization/z_score.py
	@echo "phony target $@"
data/ml_data/02b_scaled-%.csv: ph/02b_scaled-% scripts4ml/02b_data_standardization.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/02b_data_standardization.py $@
	ls data/ml_data/
	echo $@ | sed 's/\.csv/\.pkl/' | xargs test -f
	echo $@ | sed 's/\.csv/\.json/' | xargs test -f
	test -f $@

ph/03_features-%-xi2: data/ml_data/02b_scaled-%.csv ph/02b_scaled-%
	@echo "phony target $@"
data/ml_data/03_features-%.json: ph/03_features-% scripts4ml/03_feature_selection.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/03_feature_selection.py $@
	test -f $@

ph/04_model-%-ada_boost: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/ada_boost.py
	@echo "phony target $@"
ph/04_model-%-bernoulli_nb: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/bernoulli_nb.py
	@echo "phony target $@"
ph/04_model-%-decision_tree: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/decision_tree.py
	@echo "phony target $@"
ph/04_model-%-extra_trees: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/extra_trees.py
	@echo "phony target $@"
ph/04_model-%-gaussian_nb: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/gaussian_nb.py
	@echo "phony target $@"
ph/04_model-%-knc: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/knc.py
	@echo "phony target $@"
ph/04_model-%-logistic: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/logistic.py
	@echo "phony target $@"
ph/04_model-%-mlpc: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/mlpc.py
	@echo "phony target $@"
ph/04_model-%-nearest_centroid: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/nearest_centroid.py
	@echo "phony target $@"
ph/04_model-%-quadratic_discriminant: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/quadratic_discriminant.py
	@echo "phony target $@"
ph/04_model-%-random_forest: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/random_forest.py
	@echo "phony target $@"
ph/04_model-%-svc: data/ml_data/03_features-%.json ph/03_features-% scripts4ml/aux_04_model_train/svc.py
	@echo "phony target $@"
data/ml_data/04_model-%.pkl: ph/04_model-% scripts4ml/04_model_train.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/04_model_train.py $@
	test -f $@

data/ml_data/05_prediction-%.csv: data/ml_data/04_model-%.pkl scripts4ml/05_prediction.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/05_prediction.py $@
	test -f $@

data/ml_data/06_score-%.csv: data/ml_data/05_prediction-%.csv scripts4ml/06_score_by_fold.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/06_score_by_fold.py $@
	test -f $@

data/ml_data/07_global_score-%.csv: data/ml_data/06_score-0-%.csv data/ml_data/06_score-1-%.csv data/ml_data/06_score-2-%.csv data/ml_data/06_score-3-%.csv data/ml_data/06_score-4-%.csv scripts4ml/07_global_score.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/07_global_score.py $(subst data/global_score-,,$(subst .csv,,$@))

# single fold test
sample-scores: data/ml_data/merged_06_scores-0-e112.csv
	@echo "phony target $@"
data/ml_data/merged_06_scores-0-e112.csv: ph/sample_01-0
	source .venv/bin/activate; python3 scripts4ml/merge_06_scores.py
	head -n 5 $@
ph/sample_01-%: ph/sample_02-%-e112
	@echo "phony target $@"
ph/sample_02-%: ph/sample_03-%-diabetia
	@echo "phony target $@"
ph/sample_03-%: ph/sample_04-%-unbalanced
	@echo "phony target $@"
ph/sample_04-%: ph/sample_05-%-yeo_johnson ph/sample_05-%-quantile_transform
	@echo "phony target $@"
ph/sample_05-%: ph/sample_06-%-z_score
	@echo "phony target $@"
ph/sample_06-%: ph/sample_07-%-xi2
	@echo "phony target $@"
ph/sample_07-%: ph/sample_08-%-gaussian_nb ph/sample_08-%-bernoulli_nb ph/sample_08-%-nearest_centroid ph/sample_08-%-quadratic_discriminant ph/sample_08-%-extra_trees ph/sample_08-%-decision_tree ph/sample_08-%-mlpc
	@echo "phony target $@"
ph/sample_08-%: data/ml_data/06_score-%.csv
	@echo "phony target $@"

# statistical analysis
data/table_one/tbl1.csv data/table_one/tbl1.xlsx: data/diabetia.csv scripts2print/table_one/__tableOne__.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts2print/table_one/__tableOne__.py
