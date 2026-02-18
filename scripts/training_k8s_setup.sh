#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
TRAINING_K8S_PATH="$SCRIPT_DIR/../k8s/training"

# Define ml training namespace
TRAINING_NAMESPACE="ml-application-ns"

if minikube status | grep -q "host: Running"; then
    # Deploying namespace, configmap and secrets
    echo "Deploying namespace, configmap and secrets! ^@^"
    kubectl apply -f "${TRAINING_K8S_PATH}/training-namespace.yaml"
    kubectl apply -f "${TRAINING_K8S_PATH}/training-configmap.yaml"
    kubectl apply -f "${TRAINING_K8S_PATH}/training-sensor-db-credentials.yaml"
    kubectl apply -f "${TRAINING_K8S_PATH}/training-ml-artifacts-db-credentials.yaml"

    # Setting up ml database + procrastinate schema
    echo "Setting ML Database Schema! ^-^"
    bash $SCRIPT_DIR/training_upload_schema.sh

    # Wait for schema to be added to the database before taking any further actions
    echo "Waiting for schema upload to complete.............."
    kubectl wait --for=condition=complete job/ml-db-setup -n $TRAINING_NAMESPACE --timeout=180s

    # Start model training and api deployments
    echo "YAYYYYY!! Schema is ready! Deploying applications! ^.^"
    kubectl apply -f "${TRAINING_K8S_PATH}/training-apps.yaml"
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi