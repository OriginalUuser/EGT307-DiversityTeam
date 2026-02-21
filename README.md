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



## Using Makefile to build the application

You can use the `Makefile` build the pipelines. Ensure you have docker.service daemon running.

### Linux (debian based distros)

1. Run `sudo apt install build-essential`
2. Create a `.env` file in the base directory
3. Fill in values for `POSTGRES_PASS` and `ML_POSTGRES_PASS`
```.env
# Example
POSTGRES_PASS=password
ML_POSTGRES_PASS=password
```
4. Run `make` in the base directory

### MacOS

1. Run `xcode-select --install`
2. Create a `.env` file in the base directory
3. Fill in values for `POSTGRES_PASS` and `ML_POSTGRES_PASS`
```.env
# Example
POSTGRES_PASS=password
ML_POSTGRES_PASS=password
```
4. Run `make` in the base directory

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



