#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
HEADLAMP_PATH="$SCRIPT_DIR/../k8s/headlamp"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Setup the namespace
    kubectl apply -f "${HEADLAMP_PATH}/headlamp-namespace.yaml"
    kubectl apply -f "${HEADLAMP_PATH}/headlamp-service-account.yaml"
    kubectl apply -f "${HEADLAMP_PATH}/headlamp-role.yaml"
    kubectl apply -f "${HEADLAMP_PATH}/headlamp-rolebinding.yaml"
    kubectl apply -f "${HEADLAMP_PATH}/headlamp-secret.yaml"
    kubectl apply -f "${HEADLAMP_PATH}/headlamp-deployment.yaml"
    kubectl apply -f "${HEADLAMP_PATH}/headlamp-service.yaml"
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi