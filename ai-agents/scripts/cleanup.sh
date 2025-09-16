#!/bin/bash
# cleanup.sh - Resource cleanup script

set -e

echo "Cleaning up resources..."

# Load environment
if [ -f .env ]; then
    source .env
fi

# Delete Kubernetes resources
kubectl delete namespace ai-agents --ignore-not-found=true

# Delete cluster (optional)
read -p "Delete GKE cluster ${CLUSTER_NAME:-ai-boutique-hackathon}? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    gcloud container clusters delete ${CLUSTER_NAME:-ai-boutique-hackathon} \
        --region=${REGION:-us-central1} \
        --quiet
    echo "Cluster deleted!"
fi

echo "Cleanup complete!"