#!/bin/bash

kubectl kustomize "https://github.com/nginx/nginx-gateway-fabric/config/crd/gateway-api/standard?ref=v2.4.0" | kubectl apply -f -
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.19.2/cert-manager.yaml

# Wait for all the cert-manager deployments to be ready
kubectl wait --for=condition=available deployment/cert-manager -n cert-manager --timeout=300s
kubectl wait --for=condition=available deployment/cert-manager-webhook -n cert-manager --timeout=300s
kubectl wait --for=condition=available deployment/cert-manager-cainjector -n cert-manager --timeout=300s

# Create nginx-gateway namespace
kubectl apply -f ./k8s/gateway-api-nginx/gateway-namespace.yaml

# Create certifications for the NGINX Gateway Fabric
kubectl apply -f ./k8s/gateway-api-nginx/gateway-ca.yaml
kubectl apply -f ./k8s/gateway-api-nginx/gateway-servercert.yaml
kubectl apply -f ./k8s/gateway-api-nginx/gateway-agentcert.yaml

# Deploy NGINX Gateway Fabric custom resource definitions
kubectl apply --server-side -f https://raw.githubusercontent.com/nginx/nginx-gateway-fabric/v2.4.0/deploy/crds.yaml

# Deploy NGINX Gateway Fabric with NGINX Open Source and nodeSelector 
kubectl apply -f ./k8s/gateway-api-nginx/gateway-deployment.yaml

# Setup up GatewayAPI
kubectl apply -f ./k8s/gateway-api-nginx/gateway-referencegrant.yaml
kubectl apply -f ./k8s/gateway-api-nginx/gateway-gateway.yaml