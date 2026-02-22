# AquaBoard

# Project Members

### 231725Z - Darren Foo Tun Wei
### 230649F - Matthew Christopher Tan Ming Wen
### 232842C - Zhang Zhexiang
### 231606H - Pinili Johan Matthew Valdez

# Directory Structure

```
.
├── README.md
├── deployment
|   └── Dockerfiles
├── k8s
|   └── base
|       └── k8s manifests
└── apps
    └── database_app
        ├── src
        |   └── Your source code.py
        ├── test
        |   └── Your test code.py
        └── requirements.txt
```

# Project Objectives

The goal of AquaBoard is the consolidation of real-time sensor data streams in aquaponics systems.

With the onset of Singapore's goal of self-sufficiency, vertical farming methods such as aquaponics and hydroponics are increasingly relevant. This is due to the lack of land area for traditional farming methods. Hence, this project aims to supplement current and future vertical farming infrastructure through the data science. Namely, allowing for the consolidation, presentation, and analysis of data.

This project leverages Kubernetes architecture to create a scalable, available, and fault tolerant unerlying system.

# Execution Instructions

## Step 1: Prerequisite software

Requires **docker & minikube** to run and host the kubernetes cluster.

## Step 2: Installation of packages

### LINUX
1. Install required packages
```shell
# Required
sudo apt install postgresql build-essential

# For converting to unix format
sudo apt install dos2unix
```

### MAC:
1. Install required packages
```shell
# Required
brew install gettext postgresql
xcode-select --install

# For converting to unix format
brew install dos2unix
```

## Step 3: Setting up environment variables

1. Create a file named `.env` in the base directory
2. Fill in values for `POSTGRES_PASS` and `ML_POSTGRES_PASS`. These will be the passwords that will be used for the admin accounts of the databases.
```.env
# Example
POSTGRES_PASS=password
ML_POSTGRES_PASS=password
```

## Step 4. Using Makefile to build the application

Use the `Makefile` to create the all the deployments of the cluster. Ensure you have docker.service daemon running and are running commands from the base directory.

Sometimes the bash scripts will be in dos format, making them unable to be run. If this is the case, run the following command, which will convert all the bash scripts in the `./scripts` directory into unix format.
```shell
make fix-scripts
```

1. Run `make start-minikube`. This will start minikube with maximum allotments for --cpus and --memory. If you want to set a custom resource allotment, simply use the `minikube start --cpus=n --memory=n`. Note that it is recommended to use at least 8gb (8000) of RAM to ensure the cluster can run smoothly.
```shell
# Max CPUs and RAM allocations
make start-minikube

# Custom resource allotment
minikube start --cpus=X --memory=X
```

2. Run `make` to set up the entire cluster. This might take a while
```shell
make
```

3. Run `make minikube-tunnel` to create a tunnel from localhost to the Nginx GatewayAPI for accessing the dashboard, ingestion, endpoint, and the monitoring reports.
```shell
make minikube-tunnel
```

4. Run `make headlamp-service` in another terminal to create a tunnel from localhost to the headlamp NodePort.
```shell
make headlamp-service
```

5. In order to access the headlamp UI, you need to generate the headlamp token
```shell
make headlamp-token
```

## Step 5. Populating databases for testing

The `Makefile` includes extra scripts to populate the postgres databases.

1. Populating the sensor database with data from this Kaggle dataset (Ogbuokiri, 2023). This will create a k8s Job that downloads the dataset and uploads it into the sensor database
```shell
make upload-data
```

2. Populating the model artifacts database. Note that data needs to be uploaded into the database before models can be trained.
```shell
# Method 1: Force run the monitoring cronjob to trigger model retraining
kubectl create job -n monitoring-job-ns --from=cronjob/monitoring-scheduled-job test

# Method 2: Create the training job (from base directory)
kubectl apply -f ./k8s/training/training-jobs.yaml -l component=ml-force-train-job
```

---

### REGARDING MODEL INFERENCE

Refer to [model_inference_example.ipynb](test/model_inference_example.ipynb) on how to use the model for inference.

# System Architecture

## Microservice 1

...

## Microservice n

...

# Data Source

1. Ogbuokiri, B. (2023). Sensor-based Aquaponics Fish Pond Datasets (Version 1) [Data set]. Kaggle. https://www.kaggle.com/datasets/ogbuokiriblessing/sensor-based-aquaponics-fish-pond-datasets

# Limitations 





