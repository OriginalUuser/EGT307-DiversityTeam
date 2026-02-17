# !/bin/bash

# Setup
minikube addons enable metrics-server
kubectl -n kube-system apply -f https://github.com/emberstack/kubernetes-reflector/releases/latest/download/reflector.yaml
kubectl wait --for=condition=available deployment.apps/reflector -n kube-system --timeout=120s

# Startup all Database Clusters
bash ./scripts/database_k8s_setup.sh

# Upload data to Database Clusters
bash ./scripts/database_run_upload.sh

# Startup Monitoring Application
bash ./scripts/monitoring_k8s_setup.sh

# Startup Ingestion Application
bash ./scripts/ingestion_k8s_setup.sh

# Startup Training Application
bash ./scripts/training_k8s_setup.sh

# Startup Dashboard Application
bash ./scripts/dashboard_k8s_setup.sh

echo "Finished setting up k8s cluster"