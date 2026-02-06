#!/bin/bash

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    kubectl apply -f ./k8s/monitoring/monitor-namespace.yaml
    kubectl apply -f ./k8s/monitoring/monitor-config.yaml
    kubectl apply -f ./k8s/monitoring/monitor-storage.yaml
    kubectl apply -f ./k8s/monitoring/monitor-deployment.yaml
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi