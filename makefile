# short names:
create_env: .venv/bin/activate

diabetia: data/diabetia.csv

download: data/hk_database.csv

clean:
	#rm -rf data/hk_database.csv
	rm -rf data/hk_database_cleaned.csv
	#rm -rf data/diabetia.csv
	rm -rf data/fold_selection-*.json
	rm -rf data/presel-*
	rm -rf data/prebalanced-*
	rm -rf data/balanced-*.csv
	rm -rf data/normalized-*.pkl
	rm -rf data/features_selected-*.json
	rm -rf data/model-*.pkl
	rm -rf data/prediction-*.csv
	rm -rf data/score-*.csv
	rm -rf data/global_score-*.csv
	rm -rf data/table_one/tbl1.csv
	rm -rf data/table_one/tbl1.xlsx

test: data/score-0-e112-diabetia-unbalanced-zscore-xi2-logistic.csv

clean-test: clean test

# initial setup
.venv/bin/activate: bash/run_enviroment.sh requirements.txt
	bash bash/run_enviroment.sh

data/hk_database.csv:
	cd data && make hk_database.csv
	@echo "Downloaded hk_database.csv"

# Special targets
.PRECIOUS: data/diabetia.csv data/hk_database.csv data/ml_data/%
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
data/ml_data/fold_used-0-% data/ml_data/fold_used-1-% data/ml_data/fold_used-2-% data/ml_data/fold_used-3-% data/ml_data/fold_used-4-%: data/ml_data/00_folds-%.json
	@rm $@ || echo "Ready to create $@"
	touch $@

data/ml_data/prebalanced-%-diabetia: data/diabetia.csv data/ml_data/fold_used-% .venv/bin/activate
	@unlink $@ || echo "No file to unlink"
	ln -s data/diabetia.csv $@

data/ml_data/01_balanced-%-unbalanced.csv: data/ml_data/prebalanced-% scripts4ml/01_class_balancing.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/01_class_balancing.py $@
	test -f $@

data/ml_data/02_normalized-%-zscore.csv: data/ml_data/01_balanced-%.csv scripts4ml/02_data_normalization.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/02_data_normalization.py $@
	echo $@ | sed 's/\.csv/\.pkl/' | xargs test -f
	echo $@ | sed 's/\.csv/\.json/' | xargs test -f
	test -f $@

data/features_selected-%-xi2.json: data/ml_data/02_normalized-%.csv scripts4ml/03_feature_selection.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/03_feature_selection.py $@
	test -f $@

data/model-%-logistic.pkl: data/features_selected-%.json scripts4ml/04_model_train.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/04_model_train.py $@

data/prediction-%.csv: data/model-%.pkl scripts4ml/05_prediction.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/05_prediction.py $@

data/score-%.csv: data/prediction-%.csv scripts4ml/06_score_by_fold.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/06_score_by_fold.py $@

data/global_score-%.csv: scripts4ml/07_global_score.py .venv/bin/activate
	make data/score-$(subst -x-,-0-,$*).csv
	make data/score-$(subst -x-,-1-,$*).csv
	make data/score-$(subst -x-,-2-,$*).csv
	make data/score-$(subst -x-,-3-,$*).csv
	make data/score-$(subst -x-,-4-,$*).csv
	source .venv/bin/activate; python3 scripts4ml/07_global_score.py $(subst data/global_score-,,$(subst .csv,,$@))

# statistical analysis
data/table_one/tbl1.csv data/table_one/tbl1.xlsx: data/diabetia.csv scripts2print/table_one/__tableOne__.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts2print/table_one/__tableOne__.py
