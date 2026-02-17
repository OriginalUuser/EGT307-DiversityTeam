#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
TRAINING_K8S_PATH="$SCRIPT_DIR/../k8s/training"

# Define ml training namespace
TRAINING_NAMESPACE="ml-application-ns"
DB_NAMESPACE="ml-artifacts-db-ns"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Wait for database deployment to be ready
    kubectl wait --for=condition=Ready cluster/ml-artifacts-db --namespace=$DB_NAMESPACE --timeout=120s

    # Delete old job if it already exists
    kubectl delete job ml-db-setup -n $TRAINING_NAMESPACE --ignore-not-found

    # Apply database schema
    kubectl apply -f "${TRAINING_K8S_PATH}/training-jobs.yaml" -l component=ml-db-schema-initializer
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi