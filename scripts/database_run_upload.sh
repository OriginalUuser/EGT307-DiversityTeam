#!/bin/bash

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Wait for database deployment to be ready
    kubectl wait --for=condition=Ready cluster/sensor-db-ha --namespace=database-ns --timeout=120s

    # Run the data upload job
    kubectl apply -f ./k8s/database/sensor-database/postgres-job-configmap.yaml
    kubectl apply -f ./k8s/database/sensor-database/postgres-data-loader.yaml
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi