#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
INGESTION_PATH="$SCRIPT_DIR/../k8s/ingestion"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    kubectl apply -f "${INGESTION_PATH}/ingestion-namespace.yaml"
    kubectl apply -f "${INGESTION_PATH}/ingestion-dbcreds.yaml"
    kubectl apply -f "${INGESTION_PATH}/ingestion-config.yaml"
    kubectl apply -f "${INGESTION_PATH}/ingestion-deployment.yaml"
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi