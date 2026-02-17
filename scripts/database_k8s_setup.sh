#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
DATABASE_K8S_PATH="$SCRIPT_DIR/../k8s/database"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Get CloudNativePG
    kubectl apply --server-side -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.28/releases/cnpg-1.28.0.yaml
    kubectl wait --for=condition=available deployment/cnpg-controller-manager -n cnpg-system --timeout=120s
    kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=cloudnative-pg -n cnpg-system --timeout=120s

    # Setup namespace: database-ns, ml-artifacts-db-ns
    kubectl apply -f "${DATABASE_K8S_PATH}/sensor-database/postgres-namespace.yaml"
    kubectl apply -f "${DATABASE_K8S_PATH}/ml-artifacts-database/postgres-namespace.yaml"

    # Setup secrets
    envsubst < "${DATABASE_K8S_PATH}/sensor-database/postgres-credentials.yaml" | kubectl apply -f -
    envsubst < "${DATABASE_K8S_PATH}/ml-artifacts-database/postgres-credentials.yaml" | kubectl apply -f -

    # Start CloudNativePG Cluster postgresql databases
    kubectl apply -f "${DATABASE_K8S_PATH}/sensor-database/postgres-storage.yaml"
    kubectl apply -f "${DATABASE_K8S_PATH}/sensor-database/postgres-deployment.yaml"
    
    kubectl apply -f "${DATABASE_K8S_PATH}/ml-artifacts-database/postgres-storage.yaml"
    kubectl apply -f "${DATABASE_K8S_PATH}/ml-artifacts-database/postgres-deployment.yaml"
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi