.DEFAULT_GOAL := all
SHELL := /bin/bash

# Encrypt .env variables to generate kubernetes secrets
include .env
export $(shell sed 's/=.*//' .env)

# Pipelines!
all: \
	minikube-installations \
	setup-db \
	setup-monitoring \
	setup-ingestion \
	setup-training \
	training-cronjob \
	setup-dashboard \
	training-cronjob
	
rebuild: clean all

# --- Minikube startup! ---
# Build Minikube
start-minikube:
	minikube start --cpus=max --memory=max

# Minikube addons
minikube-installations:
	minikube addons enable metrics-server
	kubectl -n kube-system apply -f https://github.com/emberstack/kubernetes-reflector/releases/latest/download/reflector.yaml
	kubectl wait --for=condition=available deployment.apps/reflector -n kube-system --timeout=120s

# --- Cluster startup scripts! ---
# Setup: Database Cluster
setup-db:
	bash ./scripts/database_k8s_setup.sh
	@echo "Kubernetes database clusters are up ^^"

# Startup Monitoring Application
setup-monitoring:
	bash ./scripts/monitoring_k8s_setup.sh
	@echo "Successfully setup monitoring! ^.^"

# Startup Ingestion Application
setup-ingestion:
	bash ./scripts/ingestion_k8s_setup.sh
	@echo "Successfully setup ingestion- ^c^"

# Startup Training Application
setup-training:
	bash ./scripts/training_k8s_setup.sh
	@echo "Successfully setup training application~ >.<"

# Startup Dashboard Application
setup-dashboard:
	bash ./scripts/dashboard_k8s_setup.sh
	@echo "Successfully setup Dashboard application! ^p^"

# --- Cronjob, Data Upload & Misc scripts! ---
# Upload data to Database Clusters
upload-data:
	bash ./scripts/database_run_upload.sh
	@echo "Uploaded data! >w<"

# Starts training cronjob
training-cronjob:
	bash ./scripts/training_cronjob.sh
	@echo "Started training cronjob! >//<"

# Generate model artifacts database schema
model-artifacts-schema:
	bash ./scripts/training_upload_schema.sh
	@echo "Uploaded ml artifacts db schema! :3"

shutdown:
	minikube delete

# Tools for convenience
clean:
	@echo "Cleaning up Kubernetes resources!" --ignore-not-found
	-kubectl delete cluster ml-artifacts-db -n ml-artifacts-db-ns --ignore-not-found
	-kubectl delete cluster sensor-db-ha -n database-ns --ignore-not-found
	-kubectl delete pvc --all -n database-ns --ignore-not-found
	-kubectl delete pvc --all -n ml-artifacts-db-ns --ignore-not-found
	-kubectl delete pvc --all -n database-ns --ignore-not-found
	-kubectl delete pvc --all -n ml-application-ns --ignore-not-found
	-kubectl delete pv --all
	-kubectl delete storageclass postgres-local-disk ml-postgres-local-disk --ignore-not-found
	-kubectl delete namespaces $$(kubectl get namespaces --no-headers -o custom-columns=":metadata.name" | grep -vE 'kube-system|kube-public|kube-node-lease|default')
	@echo "Cleanup complete! >_<"