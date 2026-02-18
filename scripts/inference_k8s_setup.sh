#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
INFERENCE_PATH="$SCRIPT_DIR/../k8s/inference"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    kubectl apply -f "${INFERENCE_PATH}/inference-namespace.yaml"
    kubectl apply -f "${INFERENCE_PATH}/inference-dbcreds.yaml"
    kubectl apply -f "${INFERENCE_PATH}/inference-mlcreds.yaml"
    kubectl apply -f "${INFERENCE_PATH}/inference-config.yaml"
    kubectl apply -f "${INFERENCE_PATH}/inference-deployment.yaml"
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi