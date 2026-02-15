#!/bin/bash

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    kubectl apply -f ./k8s/dashboard/dashboard-namespace.yaml
    kubectl apply -f ./k8s/dashboard/dashboard-dbcreds.yaml
    kubectl apply -f ./k8s/dashboard/dashboard-config.yaml
    kubectl apply -f ./k8s/dashboard/dashboard-deployment.yaml
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi