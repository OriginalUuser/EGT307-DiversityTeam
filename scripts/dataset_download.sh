#!/bin/bash

# Pull kaggle dataset from kaggle hub
curl -L -o "./data/kaggle_dataset.zip" --create-dirs https://www.kaggle.com/api/v1/datasets/download/ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets
unzip -o "./data/kaggle_dataset.zip" -d "./data/kaggle_dataset_raw"
rm ./data/kaggle_dataset.zip

# # Clean dataset tables to match each other
mkdir ./data/kaggle_dataset_clean
sed -i "s/Jan-00/12.45/g" "./data/kaggle_dataset_raw/IoTPond4.csv"
python ./scripts/python_helpers/raw_dataset_cleaning.py

# Upload data to the database
python ./scripts/python_helpers/database_csv_upload.py