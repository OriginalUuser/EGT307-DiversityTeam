#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
DASHBOARD_K8S_PATH="$SCRIPT_DIR/../k8s/dashboard"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    kubectl apply -f "${DASHBOARD_K8S_PATH}/dashboard-namespace.yaml"
    kubectl apply -f "${DASHBOARD_K8S_PATH}/dashboard-dbcreds.yaml"
    kubectl apply -f "${DASHBOARD_K8S_PATH}/dashboard-config.yaml"
    kubectl apply -f "${DASHBOARD_K8S_PATH}/dashboard-deployment.yaml"
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi