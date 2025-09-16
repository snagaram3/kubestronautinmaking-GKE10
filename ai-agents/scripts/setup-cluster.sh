#!/bin/bash
# setup-cluster.sh - GKE cluster setup script

set -e

echo "Setting up GKE cluster..."

# Load environment
if [ -f .env ]; then
    source .env
fi

# Create cluster
gcloud container clusters create-auto ${CLUSTER_NAME:-ai-boutique-hackathon} \
    --region=${REGION:-us-central1} \
    --release-channel=rapid \
    --enable-autoscaling

# Get credentials
gcloud container clusters get-credentials ${CLUSTER_NAME:-ai-boutique-hackathon} \
    --region=${REGION:-us-central1}

echo "Cluster setup complete!"