#!/bin/bash

# Pull kaggle dataset from kaggle hub
curl -L -o "./database_vol/kaggle_dataset.zip" --create-dirs https://www.kaggle.com/api/v1/datasets/download/ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets
unzip "./database_vol/kaggle_dataset.zip" -d "./database_vol/kaggle_dataset"
rm ./database_vol/kaggle_dataset.zip

# THIS CODE IS FOR SQLITE DB
# # Convert .csv files into Sqlite3 .db file
# index=0
# for CSV_FILE in "./database_vol/kaggle_dataset"/* ; do
#     if [[ -f "$CSV_FILE" && "$CSV_FILE" == *.csv ]]; then
#         echo "$CSV_FILE"
#         TABLE_NAME="iot_pond_$index"
#         sqlite3 "./database_vol/sensor_readings.db" ".mode csv" ".import $CSV_FILE $TABLE_NAME" ".exit"
#         ((index++))
#     fi
# done

# # Clean dataset tables to match each other
# python ./scripts/raw_dataset_cleaning.py