#!/bin/bash
# simple-prometheus-setup.sh - Complete Prometheus and Grafana setup in one script
# Configured with minimal resource requirements for cost optimization

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="monitoring"
RELEASE_NAME="prometheus"
GRAFANA_PASSWORD="admin123"

echo -e "${BLUE}🚀 Simple Prometheus and Grafana Setup for GKE${NC}"
echo "=================================================="

# Step 1: Prerequisites check
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl is not installed${NC}"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo -e "${RED}❌ helm is not installed${NC}"
    echo "Installing Helm..."
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ kubectl is not configured or cluster is not accessible${NC}"
    echo "Please run: gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE --project PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"

# Step 2: Setup Helm repo
echo -e "\n${YELLOW}📦 Setting up Helm repository...${NC}"
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts >/dev/null 2>&1
helm repo update >/dev/null 2>&1
echo -e "${GREEN}✅ Helm repository configured${NC}"

# Step 3: Create namespace
echo -e "\n${YELLOW}🏗️ Creating monitoring namespace...${NC}"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f - >/dev/null
echo -e "${GREEN}✅ Namespace created${NC}"

# Step 4: Create minimal values file
echo -e "\n${YELLOW}⚙️ Creating minimal configuration...${NC}"
cat > /tmp/minimal-prometheus-values.yaml << 'EOF'
# Minimal resource configuration for Prometheus stack
prometheus:
  service:
    type: ClusterIP
  prometheusSpec:
    # Minimal resources
    resources:
      requests:
        memory: "400Mi"
        cpu: "200m"
      limits:
        memory: "800Mi"
        cpu: "500m"
    # Small storage
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 2Gi
    # Short retention
    retention: 7d
    retentionSize: 1GB
    # Enable service discovery
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false

grafana:
  service:
    type: ClusterIP
  adminPassword: admin123
  # Minimal resources
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "200m"
  # Small storage
  persistence:
    enabled: true
    size: 1Gi
  # Essential dashboards only
  dashboards:
    default:
      kubernetes-overview:
        gnetId: 315
        revision: 3
        datasource: Prometheus
      pods-overview:
        gnetId: 6417
        revision: 1
        datasource: Prometheus

alertmanager:
  service:
    type: ClusterIP
  alertmanagerSpec:
    # Minimal resources
    resources:
      requests:
        memory: "64Mi"
        cpu: "50m"
      limits:
        memory: "128Mi"
        cpu: "100m"
    storage:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 1Gi

# Disable unnecessary components for minimal setup
kubeStateMetrics:
  resources:
    requests:
      memory: "64Mi"
      cpu: "50m"
    limits:
      memory: "128Mi"
      cpu: "100m"

nodeExporter:
  resources:
    requests:
      memory: "32Mi"
      cpu: "25m"
    limits:
      memory: "64Mi"
      cpu: "50m"

prometheusOperator:
  resources:
    requests:
      memory: "64Mi"
      cpu: "50m"
    limits:
      memory: "128Mi"
      cpu: "100m"
EOF

echo -e "${GREEN}✅ Minimal configuration created${NC}"

# Step 5: Deploy Prometheus stack
echo -e "\n${YELLOW}🚀 Deploying Prometheus stack (this may take a few minutes)...${NC}"
helm upgrade --install $RELEASE_NAME prometheus-community/kube-prometheus-stack \
  --namespace $NAMESPACE \
  --values /tmp/minimal-prometheus-values.yaml \
  --wait --timeout=600s

echo -e "${GREEN}✅ Prometheus stack deployed successfully${NC}"

# Step 6: Wait for pods to be ready
echo -e "\n${YELLOW}⏳ Waiting for all pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/instance=$RELEASE_NAME" -n $NAMESPACE --timeout=300s >/dev/null 2>&1

echo -e "${GREEN}✅ All pods are ready${NC}"

# Step 7: Create ServiceMonitor for microservices
echo -e "\n${YELLOW}🔍 Creating ServiceMonitor for microservices...${NC}"
kubectl apply -f - << 'EOF'
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: microservices-monitor
  namespace: monitoring
  labels:
    app: microservices-monitor
spec:
  selector:
    matchLabels:
      monitoring: "enabled"
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
  - port: http
    interval: 30s
    path: /metrics
  namespaceSelector:
    matchNames:
    - default
    - microservices
    - kube-system
EOF

echo -e "${GREEN}✅ ServiceMonitor created${NC}"

# Step 8: Display status and access information
echo -e "\n${BLUE}📊 Deployment Summary${NC}"
echo "======================"

# Show resource usage
echo -e "\n${YELLOW}Resource Usage:${NC}"
kubectl top pods -n $NAMESPACE 2>/dev/null || echo "Metrics not available yet (normal for new deployments)"

# Show services
echo -e "\n${YELLOW}Services:${NC}"
kubectl get svc -n $NAMESPACE

# Show pods
echo -e "\n${YELLOW}Pods Status:${NC}"
kubectl get pods -n $NAMESPACE -o wide

# Cleanup temp file
rm -f /tmp/minimal-prometheus-values.yaml

# Step 9: Access instructions
echo -e "\n${GREEN}🎉 Setup Complete!${NC}"
echo "=================="
echo ""
echo -e "${BLUE}Access Information:${NC}"
echo "-------------------"
echo ""
echo -e "${YELLOW}Prometheus:${NC}"
echo "  Command: kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-kube-prometheus-prometheus 9090:9090"
echo "  URL:     http://localhost:9090"
echo ""
echo -e "${YELLOW}Grafana:${NC}"
echo "  Command: kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-grafana 3000:80"
echo "  URL:     http://localhost:3000"
echo "  Login:   admin / $GRAFANA_PASSWORD"
echo ""
echo -e "${YELLOW}AlertManager:${NC}"
echo "  Command: kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-kube-prometheus-alertmanager 9093:9093"
echo "  URL:     http://localhost:9093"

# Function to start all port forwards
start_all_forwards() {
    echo -e "\n${YELLOW}🚀 Starting all port forwards...${NC}"
    
    # Kill any existing forwards
    pkill -f "kubectl port-forward.*$NAMESPACE" 2>/dev/null || true
    sleep 2
    
    # Start forwards
    kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-kube-prometheus-prometheus 9090:9090 > /dev/null 2>&1 &
    PROM_PID=$!
    
    kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-grafana 3000:80 > /dev/null 2>&1 &
    GRAFANA_PID=$!
    
    kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-kube-prometheus-alertmanager 9093:9093 > /dev/null 2>&1 &
    ALERT_PID=$!
    
    echo -e "${GREEN}✅ Port forwarding active:${NC}"
    echo "  - Prometheus: http://localhost:9090 (PID: $PROM_PID)"
    echo "  - Grafana:    http://localhost:3000 (PID: $GRAFANA_PID)"
    echo "  - AlertMgr:   http://localhost:9093 (PID: $ALERT_PID)"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all port forwards${NC}"
    
    trap "kill $PROM_PID $GRAFANA_PID $ALERT_PID 2>/dev/null || true; echo; echo 'Port forwarding stopped'; exit" INT
    wait
}

# Step 10: Instructions for microservices
echo ""
echo -e "${BLUE}🎯 Configure Your Microservices:${NC}"
echo "--------------------------------"
echo ""
echo "1. Add annotations to your microservice pods:"
echo "   annotations:"
echo "     prometheus.io/scrape: \"true\""
echo "     prometheus.io/port: \"8080\""
echo "     prometheus.io/path: \"/metrics\""
echo ""
echo "2. Or label your services:"
echo "   kubectl label service YOUR_SERVICE monitoring=enabled"
echo ""

# Ask to start port forwarding
echo -e "${YELLOW}Would you like to start port forwarding now? (y/n):${NC} "
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    start_all_forwards
else
    echo ""
    echo -e "${GREEN}💡 Setup complete! Use the commands above to access your monitoring stack.${NC}"
    echo ""
    echo -e "${BLUE}Quick start commands:${NC}"
    echo "  # Access Grafana"
    echo "  kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-grafana 3000:80"
    echo ""
    echo "  # Access Prometheus"
    echo "  kubectl port-forward -n $NAMESPACE svc/$RELEASE_NAME-kube-prometheus-prometheus 9090:9090"
    echo ""
    echo -e "${YELLOW}Total estimated resource usage: ~1.5GB RAM, ~1 CPU core${NC}"
fi