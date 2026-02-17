#!/bin/bash

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Setup the namespace
    kubectl apply -f ./k8s/monitoring/monitor-namespace.yaml

    # Monitoring Application
    kubectl apply -f ./k8s/monitoring/monitor-dbcreds.yaml
    kubectl apply -f ./k8s/monitoring/monitor-config.yaml
    kubectl apply -f ./k8s/monitoring/monitor-storage.yaml
    kubectl apply -f ./k8s/monitoring/monitor-deployment.yaml

    # Monitoring CronJob
    kubectl apply -f ./k8s/monitoring/monitor-serviceacc.yaml
    kubectl apply -f ./k8s/monitoring/monitor-cronjob.yaml
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi