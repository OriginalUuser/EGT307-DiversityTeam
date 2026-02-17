#!/bin/bash

# Pull kaggle dataset from kaggle hub
curl -L -o "/app/data/kaggle_dataset.zip" --create-dirs https://www.kaggle.com/api/v1/datasets/download/ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets
unzip -o "/app/data/kaggle_dataset.zip" -d "./data/kaggle_dataset_raw"
rm /app/data/kaggle_dataset.zip

# # Clean dataset tables to match each other
mkdir /app/data/kaggle_dataset_clean
python /app/scripts/python_helpers/raw_dataset_cleaning.py

# Upload data to the database
python /app/scripts/python_helpers/database_csv_upload.py