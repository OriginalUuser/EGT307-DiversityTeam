#!/bin/bash

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Get CloudNativePG
    kubectl apply --server-side -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.28/releases/cnpg-1.28.0.yaml
    kubectl wait --for=condition=available deployment/cnpg-controller-manager -n cnpg-system --timeout=120s
    kubectl wait --for=condition=Ready pod -l app.kubernetes.io/name=cloudnative-pg -n cnpg-system --timeout=120s

    # Setup namespace: database-ns, ml-artifacts-db-ns
    kubectl apply -f ./k8s/database/sensor-database/postgres-namespace.yaml
    kubectl apply -f ./k8s/database/ml-artifacts-database/postgres-namespace.yaml

    # Setup secrets
    envsubst < ./k8s/database/sensor-database/postgres-credentials.yaml | kubectl apply -f -
    envsubst < ./k8s/database/ml-artifacts-database/postgres-credentials.yaml | kubectl apply -f -

    # Start CloudNativePG Cluster postgresql databases
    kubectl apply -f ./k8s/database/sensor-database/postgres-storage.yaml
    kubectl apply -f ./k8s/database/sensor-database/postgres-deployment.yaml
    
    kubectl apply -f ./k8s/database/ml-artifacts-database/postgres-storage.yaml
    kubectl apply -f ./k8s/database/ml-artifacts-database/postgres-deployment.yaml
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi