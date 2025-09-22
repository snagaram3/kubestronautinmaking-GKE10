#!/bin/bash
set -e

# 1️⃣ Set variables
NAMESPACE="monitoring"

# 2️⃣ Create namespace
kubectl create namespace $NAMESPACE || echo "Namespace $NAMESPACE already exists"

# 3️⃣ Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 4️⃣ Install Prometheus
helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace $NAMESPACE

# 5️⃣ Install Grafana
helm upgrade --install grafana grafana/grafana \
  --namespace $NAMESPACE

# 6️⃣ Wait for pods to be ready
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=Ready pods --all -n $NAMESPACE --timeout=300s

# 7️⃣ Output service info
echo "Prometheus and Grafana deployed in namespace '$NAMESPACE'."
kubectl get svc -n $NAMESPACE

# 8️⃣ Port-forward Grafana for local access
echo "Forwarding Grafana to http://localhost:3000 ..."
echo "Use CTRL+C to stop forwarding."
kubectl port-forward svc/grafana 3000:80 -n $NAMESPACE
