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

test: data/global_score-e112-x-diabetia-unbalanced-zscore-xi2-logistic.csv

clean-test: clean test

# initial setup
.venv/bin/activate: bash/run_enviroment.sh requirements.txt
	bash bash/run_enviroment.sh

data/hk_database.csv:
	cd data && make hk_database.csv
	@echo "Downloaded hk_database.csv"

# Special targets
.PRECIOUS: data/diabetia.csv data/hk_database.csv
.INTERMEDIATE: data/hk_database_cleaned.csv

# preprocess data
data/hk_database_cleaned.csv: data/hk_database.csv preprocess/01_engineering.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/01_engineering.py

data/diabetia.csv: data/hk_database_cleaned.csv preprocess/02_imputation.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/02_imputation.py

data/fold_selection-%.json: data/diabetia.csv preprocess/03_fold_selection.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/03_fold_selection.py $*

# Machine learning
data/presel-%-0 data/presel-%-1 data/presel-%-2 data/presel-%-3 data/presel-%-4: data/fold_selection-%.json
	@rm $@ || echo "Ready to create $@"
	touch $@

data/prebalanced-%-diabetia: data/diabetia.csv data/presel-% .venv/bin/activate
	@unlink data/prebalanced-$*-diabetia || echo "No file to unlink"
	ln -s data/diabetia.csv data/prebalanced-$*-diabetia

data/balanced-%-unbalanced.csv: data/prebalanced-% scripts4ml/01_class_balancing.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/01_class_balancing.py $(subst data/balanced-,,$(subst .csv,,$@))

data/normalized-%-zscore.pkl: data/balanced-%.csv
	echo "Normalizing data"

data/features_selected-%-xi2.json: data/normalized-%.pkl scripts4ml/03_feature_selection.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/03_feature_selection.py $(subst data/features_selected-,,$(subst .json,,$@))

data/model-%-logistic.pkl: data/features_selected-%.json scripts4ml/04_model_train.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/04_model_train.py $(subst data/model-,,$(subst .pkl,,$@))

data/prediction-%.csv: data/model-%.pkl scripts4ml/05_prediction.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/05_prediction.py $(subst data/prediction-,,$(subst .csv,,$@))

data/score-%.csv: data/prediction-%.csv scripts4ml/06_score_by_fold.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts4ml/06_score_by_fold.py $(subst data/score-,,$(subst .csv,,$@))

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
