.DEFAULT_GOAL := all
SHELL := /bin/bash

# Database ENV
DB_NAMESPACE := database-ns
DATABASE_APP_PATH := ./apps/database_app
DATABASE_UPLOAD_IMG := dvs/upload_data:v1
DATABASE_K8S_PATH := ./k8s/database

# Training ENV
TRAINING_NAMESPACE := ml-application-ns
TRAINING_K8S_PATH := ./k8s/training
TRAINING_APP_PATH := ./apps/training_app
TRAINING_INIT_IMG := dvs/ml-db-init:v1
TRAINING_WORKER_IMG := dvs/ml-trainer-worker:v1

# Encrypt .env variables to generate kubernetes secrets
include .env
export $(shell sed 's/=.*//' .env)

# Pipelines!
db_cluster: setup-db upload-data
training_pipeline: build-load-training-images deploy-training-pods
all: k8s-secrets db_cluster training_pipeline
rebuild: clean all

# We do this to minimize latency by preventing copying the entire image to minikube
DOCKER_BUILD = eval $$(minikube docker-env) && docker build

# Verify credentials to access database
k8s-secrets:
	@USERNAME_B64=$$(echo -n $(DB_USERNAME) | base64) \
	PASSWORD_B64=$$(echo -n $(DB_PASSWORD) | base64) \
	envsubst '$$USERNAME_B64 $$PASSWORD_B64' < $(TRAINING_K8S_PATH)/training-credentials.template > $(TRAINING_K8S_PATH)/training-credentials.yaml
	@echo "Credentials generated from .env! >//<"

# Setup: Database Cluster
setup-db:
	bash $(DATABASE_APP_PATH)/src/scripts/database_k8s_setup.sh
	@echo "Waiting for pods to be ready >.<"
	sleep 10
	kubectl wait --for=condition=Ready pod -l cnpg.io/cluster=sensor-db-ha,cnpg.io/podRole=instance -n $(DB_NAMESPACE) --timeout=60s
	kubectl get pods -n $(DB_NAMESPACE)
	@echo "Kubernetes database cluster is up ^^"

upload-data:
	$(DOCKER_BUILD) -t $(DATABASE_UPLOAD_IMG) -f $(DATABASE_APP_PATH)/dockerfiles/Dockerfile $(DATABASE_APP_PATH)/src
	-kubectl delete job ml-data-loader -n $(DB_NAMESPACE) 2>/dev/null || true
	kubectl apply -f $(DATABASE_K8S_PATH)/postgres-configmap.yaml
	kubectl apply -f $(DATABASE_K8S_PATH)/postgres-credentials.yaml
	UPLOAD_DATA_WORKER=$(DATABASE_UPLOAD_IMG) \
	envsubst '$${UPLOAD_DATA_WORKER}' < $(DATABASE_K8S_PATH)/postgres-data-loader.yaml | kubectl apply -f -
	@echo "Uploaded data! ^^"

# Setup: Training piplene
build-load-training-images:
	@echo "Building training images!"
	$(DOCKER_BUILD) -t $(TRAINING_INIT_IMG) -f $(TRAINING_APP_PATH)/dockerfiles/Dockerfile.init_ml_db $(TRAINING_APP_PATH)/src
	$(DOCKER_BUILD) -t $(TRAINING_WORKER_IMG) -f $(TRAINING_APP_PATH)/dockerfiles/Dockerfile.init_model_trainer_scheduler $(TRAINING_APP_PATH)/src

deploy-training-pods:
	-kubectl delete job ml-db-setup -n $(TRAINING_NAMESPACE) 2>/dev/null || true
	-kubectl wait --for=delete job/ml-db-setup -n $(TRAINING_NAMESPACE) --timeout=60s
	kubectl apply -f $(TRAINING_K8S_PATH)/training-namespace.yaml
	kubectl apply -f $(TRAINING_K8S_PATH)/training-configmap.yaml -n $(TRAINING_NAMESPACE)
	kubectl apply -f $(TRAINING_K8S_PATH)/training-credentials.yaml -n $(TRAINING_NAMESPACE)
	export UPLOAD_INIT_WORKER=$(TRAINING_INIT_IMG); \
	export UPLOAD_TRAINING_WORKER=$(TRAINING_WORKER_IMG); \
	envsubst '$${UPLOAD_INIT_WORKER} $${UPLOAD_TRAINING_WORKER}' < $(TRAINING_K8S_PATH)/training-jobs.yaml | kubectl apply -f -
	export UPLOAD_TRAINING_WORKER=$(TRAINING_WORKER_IMG); \
	envsubst '$${UPLOAD_TRAINING_WORKER}' < $(TRAINING_K8S_PATH)/training-apps.yaml | kubectl apply -f -
	kubectl get pods -n $(TRAINING_NAMESPACE)
	@echo "Training pods deployed! >.<"

# Tools for convenience
clean:
	@echo "Cleaning up Kubernetes resources!"
	-kubectl delete cluster sensor-db-ha -n $(DB_NAMESPACE) --ignore-not-found
	-kubectl delete pvc --all -n $(DB_NAMESPACE) --ignore-not-found
	-kubectl delete pvc --all -n $(TRAINING_NAMESPACE) --ignore-not-found
	-kubectl delete namespace $(DB_NAMESPACE) $(TRAINING_NAMESPACE) --ignore-not-found
	-kubectl delete pv --all --wait=false
	@echo "Removing Docker and Minikube images!"
	-eval $$(minikube docker-env) && docker rmi $(DATABASE_UPLOAD_IMG) $(TRAINING_INIT_IMG) $(TRAINING_WORKER_IMG) 2>/dev/null || true
	@echo "Cleanup complete! >_<"