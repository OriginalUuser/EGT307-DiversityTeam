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
	setup-dashboard \
	setup-gatewayapi
	
rebuild: clean all

# --- Minikube! ---
# Build Minikube
start-minikube:
	minikube start --cpus=max --memory=max

shutdown:
	minikube delete

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

# Startup GatewayAPI
setup-gatewayapi:
	bash ./scripts/gatewayapi_k8s_setup.sh
	@echo "Successfully setup GatewayAPI! ;^;"

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

# Create minikube service
minikube-tunnel:
	minikube service gateway-api-nginx -n nginx-gateway
	
# Setup Headlamp monitoring
headlamp:
	bash ./scripts/headlamp_monitoring.sh
	@echo "Started Headlamp! ⋆｡°✩"
	kubectl wait --for=condition=Ready pod -l k8s-app=headlamp -n headlamp-ns --timeout=120s
	@echo "Headlamp pod is ready! ⋆｡°✩"
	minikube service headlamp -n headlamp-ns

headlamp-token:
	@echo "Headlamp token! ⋆˚꩜｡"
	kubectl -n headlamp-ns get secret headlamp-admin -o go-template='{{.data.token | base64decode}}'

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
