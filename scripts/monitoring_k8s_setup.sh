#!/bin/bash

# Ensures dynamic pathing irregardless of directory script is run in
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
MONITORING_PATH="$SCRIPT_DIR/../k8s/monitoring"

# Check the status of minikube
if minikube status | grep -q "host: Running"; then
    # Setup the namespace
    kubectl apply -f "${MONITORING_PATH}/monitor-namespace.yaml"

    # Monitoring Application
    kubectl apply -f "${MONITORING_PATH}/monitor-namespace.yaml"

    # Configurations
    kubectl apply -f "${MONITORING_PATH}/monitor-dbcreds.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-config.yaml"

    # Run procrastinate setup job
    kubectl wait --for=condition=Ready cluster/sensor-db-ha --namespace=database-ns --timeout=120s
    kubectl apply -f "${MONITORING_PATH}/monitor-setup-jobs.yaml"
    kubectl wait --for=condition=complete job/monitoring-setup -n monitoring-ns --timeout=240s

    # Storage
    kubectl apply -f "${MONITORING_PATH}/monitor-storage.yaml"

    # Deployments
    kubectl apply -f "${MONITORING_PATH}/monitor-deployment-front.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-deployment-middle.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-deployment-back.yaml"

    # Monitoring CronJob
    kubectl apply -f "${MONITORING_PATH}/monitor-serviceacc.yaml"
    kubectl apply -f "${MONITORING_PATH}/monitor-cronjob.yaml"

else
    echo "Minikube is not running. Aborting script execution."
    exit 1
fi