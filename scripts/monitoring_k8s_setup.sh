#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
MONITORING_PATH="$SCRIPT_DIR/../k8s/monitoring"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Setup the namespace
    kubectl apply -f "${MONITORING_PATH}/monitor-namespace.yaml"

    # Monitoring Application
    kubectl apply -f "${MONITORING_PATH}/monitor-namespace.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-dbcreds.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-config.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-storage.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-deployment.yaml"

    # Monitoring CronJob
    kubectl apply -f "${MONITORING_PATH}/monitor-serviceacc.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-cronjob.yaml"

else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi