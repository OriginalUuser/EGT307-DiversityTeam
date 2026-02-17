#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
DATABASE_K8S_PATH="$SCRIPT_DIR/../k8s/database"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Wait for database deployment to be ready
    kubectl wait --for=condition=Ready cluster/sensor-db-ha --namespace=database-ns --timeout=120s

    # Run the data upload job
    kubectl apply -f "${DATABASE_K8S_PATH}/sensor-database/postgres-job-configmap.yaml"
    kubectl apply -f "${DATABASE_K8S_PATH}/sensor-database/postgres-data-loader.yaml"
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi