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

# Execution Instructions
1. Requires docker & minikube to run (This is for you, Matthew Christopher Tan Ming Wen, admin number: 230649F <3)

## Needed packages:

LINUX
1. Install packages `sudo apt install postgresql`
2. If needed, convert bash file formats: `sudo apt install dos2unix` -> `dos2unix path/to/bash-file`

MAC:
1. Install packages `brew install gettext postgresql`

## How to set up the database

1. Run `export POSTGRES_PASS=password` to set up the password that the database will use (does not matter what the password is)
1. Run `bash ./scripts/database_k8s_setup.sh`
2. Once the cluster has finished setting up (pods are running), Run `kubectl port-forward svc/sensor-db-ha-rw 5432:5432 -n database-ns`
3. Run `pip install -r db-requirements.txt`
3. Run `bash ./scripts/dataset_download.sh`

Congratulations, you have started the kubernetes database cluster!!!

Check `test\database.ipynb` for how to access and use the database locally or within the cluster.

---

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


