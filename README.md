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

Requires docker & minikube to run to host the kubernetes cluster.

## Step 2: Installation of packages

LINUX
1. Install required packages `sudo apt install postgresql build-essential dos2unix`

MAC:
1. Install packages `brew install gettext postgresql`
2. Run `xcode-select --install`

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

1. Run `make start-minikube`. This will start minikube with maximum allotments for --cpus and --memory. If you want to set a custom resource allotment, simply use the `minikube start --cpus=n --memory=n`. Note that it is recommended to use at least 8gb (8000) of RAM to ensure the cluster can run smoothly.
2. Run `make` to set up the entire cluster. This might take a while
3. OPTIONAL: To populate the sensor database for testing purposes, run `make upload-data`. This will create a job that downloads the Kaggle aquaponics dataset and uploads it into the sensor database.
4. Run `make minikube-tunnel` to create a tunnel from localhost to the Nginx GatewayAPI for accessing the dashboard, ingestion, endpoint, and the monitoring reports. It will also create a tunnel to the headlamp NodePort for monitoring the Kubernetes cluster.

---

### REGARDING MODEL INFERENCE

Refer to [model_inference_example.ipynb](test/model_inference_example.ipynb) on how to use the model for inference.

# System Architecture

## Microservice 1

...

## Microservice n

...

# Data Source


# Limitations 




