#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
TRAINING_K8S_PATH="$SCRIPT_DIR/../k8s/training"

if minikube status | grep -q "host: Running"; then
    # Wait for ml-trainer deployment to be ready
    kubectl rollout status deployment/ml-trainer -n ml-application-ns --timeout=120s

    # Start Cronjob
    kubectl apply -f "${TRAINING_K8S_PATH}/training-jobs.yaml" -l component=ml-cronjob-initializer
else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi