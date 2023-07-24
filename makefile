create_env:
	bash run_enviroment.sh

download: data/hk_database.csv
	@echo "Downloaded hk_database.csv"

data/hk_database.csv:
	cd data && make hk_database.csv
	@echo "Downloaded hk_database.csv"

# Special targets
.PRECIOUS: data/diabetia.csv data/hk_database.csv

# preprocess data
data/hk_database_cleaned.csv: data/hk_database.csv preprocess/engineering.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/engineering.py

data/diabetia.csv: data/hk_database_cleaned.csv preprocess/imputation.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/imputation.py

data/fold_selection-%.json: data/diabetia.csv preprocess/fold_selection.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/fold_selection.py