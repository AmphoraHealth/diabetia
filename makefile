download: data/hk_database.csv
	@echo "Downloaded hk_database.csv"

data/hk_database.csv:
	cd data && make hk_database.csv
