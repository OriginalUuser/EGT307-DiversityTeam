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

## How to set up the database

1. Run `export POSTGRES_PASS=password` to set up the password that the database will use (does not matter what the password is)
1. Run `.\scripts\database_k8s_setup.sh`
2. Once the cluster has finished setting up (pods are running), Run `kubectl port-forward svc/sensor-db-ha-rw 5432:5432`
3. Run `pip install -r db-requirements.txt`
3. Run `.\scripts\dataset_download.sh`

Congratulations, you have started the kubernetes database cluster!!!

Check `test\database.ipynb` for how to access and use the database locally or within the cluster.

# System Architecture

## Microservice 1

...

## Microservice n

...

# Data Source

# Limitations 