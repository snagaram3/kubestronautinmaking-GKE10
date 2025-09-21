#!/bin/bash
# setup-monitoring.sh - Script to deploy and access Prometheus/Grafana

set -e

echo "🚀 Setting up Prometheus and Grafana monitoring on GKE cluster..."

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl is not configured or cluster is not accessible"
    echo "Please run: gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE --project PROJECT_ID"
    exit 1
fi

# Initialize and apply Terraform
echo "📦 Deploying monitoring stack with Terraform..."
terraform init
terraform plan
terraform apply -auto-approve

# Wait for pods to be ready
echo "⏳ Waiting for monitoring pods to be ready..."
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/name=prometheus" -n monitoring --timeout=300s
kubectl wait --for=condition=ready pod -l "app.kubernetes.io/name=grafana" -n monitoring --timeout=300s

echo "✅ Monitoring stack deployed successfully!"

# Get service information
echo "📊 Getting service information..."
kubectl get svc -n monitoring

echo ""
echo "🔗 Access Information:"
echo "======================="
echo ""
echo "Prometheus:"
echo "- Port forward command: kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo "- URL: http://localhost:9090"
echo ""
echo "Grafana:"
echo "- Port forward command: kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
echo "- URL: http://localhost:3000"
echo "- Username: admin"
echo "- Password: admin123"
echo ""

# Function to start port forwarding
start_port_forwarding() {
    echo "🚀 Starting port forwarding for monitoring services..."
    
    # Kill any existing port forwards
    pkill -f "kubectl port-forward.*monitoring" 2>/dev/null || true
    sleep 2
    
    # Start Prometheus port forwarding in background
    kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
    PROMETHEUS_PID=$!
    
    # Start Grafana port forwarding in background
    kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &
    GRAFANA_PID=$!
    
    echo "✅ Port forwarding started:"
    echo "  - Prometheus: http://localhost:9090 (PID: $PROMETHEUS_PID)"
    echo "  - Grafana: http://localhost:3000 (PID: $GRAFANA_PID)"
    echo ""
    echo "Press Ctrl+C to stop port forwarding"
    
    # Wait for interrupt
    trap "kill $PROMETHEUS_PID $GRAFANA_PID 2>/dev/null || true; exit" INT
    wait
}

# Ask user if they want to start port forwarding
read -p "Do you want to start port forwarding now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    start_port_forwarding
else
    echo "💡 You can manually start port forwarding using the commands above"
    echo "💡 To apply microservice monitoring, label your services with 'monitoring: enabled'"
    echo "   Example: kubectl label service MY_SERVICE monitoring=enabled"
fi