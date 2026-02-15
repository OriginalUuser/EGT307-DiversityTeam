#!/bin/bash

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    kubectl apply -f ./k8s/ingestion/ingestion-namespace.yaml
    kubectl apply -f ./k8s/ingestion/ingestion-dbcreds.yaml
    kubectl apply -f ./k8s/ingestion/ingestion-config.yaml
    kubectl apply -f ./k8s/ingestion/ingestion-deployment.yaml
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi