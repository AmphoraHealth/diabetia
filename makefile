# short names:
create_env: .venv/bin/activate

diabetia: data/diabetia.csv

download: data/hk_database.csv

clean:
	rm -rf data/ml_data/0*
	rm -rf data/ml_data/fold_used-*
	rm -rf data/ml_data/prebalanced-*

test: data/ml_data/06_score-0-e112-diabetia-unbalanced-yeo_johnson-z_score-xi2-logistic.csv

clean-test: clean test

# initial setup
.venv/bin/activate: bash/run_enviroment.sh requirements.txt
	bash bash/run_enviroment.sh

data/hk_database.csv:
	cd data && make hk_database.csv
	@echo "Downloaded hk_database.csv"

# Special targets
.PRECIOUS: data/diabetia.csv data/hk_database.csv data/ml_data/00_folds-%.json data/ml_data/fold_used-% data/ml_data/01_balanced-%.csv data/ml_data/02a_normalized-%.csv data/ml_data/03_features-%.json data/ml_data/05_prediction-%.csv
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
ph/02a_normalized-%-quantile: data/ml_data/01_balanced-%.csv ph/01_balanced-% scripts4ml/aux_02a_data_normalization/quantile.py
	@echo "phony target $@"
data/ml_data/02a_normalized-%.csv: ph/02a_normalized-% scripts4ml/02a_data_normalization.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/02a_data_normalization.py $@
	ls data/ml_data/
	echo $@ | sed 's/\.csv/\.pkl/' | xargs test -f
	echo $@ | sed 's/\.csv/\.json/' | xargs test -f
	test -f $@

ph/02b_scaled-%-z_score: data/ml_data/02a_normalized-%.csv ph/02a_normalized-%
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

ph/04_model-%-logistic: data/ml_data/03_features-%.json ph/03_features-%
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

# statistical analysis
data/table_one/tbl1.csv data/table_one/tbl1.xlsx: data/diabetia.csv scripts2print/table_one/__tableOne__.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts2print/table_one/__tableOne__.py
