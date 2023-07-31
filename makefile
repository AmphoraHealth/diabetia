# short names:
create_env: .venv/bin/activate

diabetia: data/diabetia.csv

download: data/hk_database.csv

# initial setup
.venv/bin/activate: bash/run_enviroment.sh requirements.txt
	bash bash/run_enviroment.sh

data/hk_database.csv:
	cd data && make hk_database.csv
	@echo "Downloaded hk_database.csv"

# Special targets
.PRECIOUS: data/diabetia.csv data/hk_database.csv

# preprocess data
data/hk_database_cleaned.csv: data/hk_database.csv preprocess/01_engineering.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/01_engineering.py

data/diabetia.csv: data/hk_database_cleaned.csv preprocess/02_imputation.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/02_imputation.py

data/fold_selection-%.json: data/diabetia.csv preprocess/03_fold_selection.py .venv/bin/activate
	source .venv/bin/activate; python3 preprocess/03_fold_selection.py

# statistical analysis
data/table_one/tbl1.csv data/table_one/tbl1.xlsx: data/diabetia.csv scripts2print/table_one/__tableOne__.py .venv/bin/activate
	source .venv/bin/activate; python3 scripts2print/table_one/__tableOne__.py