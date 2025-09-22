#!/bin/bash
set -e

echo "🚀 Building and deploying AI components..."

# Get current project info
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1"

echo "📋 Using Project: $PROJECT_ID"

# Build Docker images
echo "🔨 Building Docker images..."
docker build -f docker/Dockerfile.customer-service-agent -t $REGION-docker.pkg.dev/$PROJECT_ID/boutique-ai-repo/customer-service-agent:latest .
docker build -f docker/Dockerfile.chat-gateway -t $REGION-docker.pkg.dev/$PROJECT_ID/boutique-ai-repo/chat-gateway:latest .

# Push images
echo "📤 Pushing images..."
docker push $REGION-docker.pkg.dev/$PROJECT_ID/boutique-ai-repo/customer-service-agent:latest
docker push $REGION-docker.pkg.dev/$PROJECT_ID/boutique-ai-repo/chat-gateway:latest

# Deploy AI components
echo "🚀 Deploying AI components..."
envsubst < k8s-manifests/customer-service-agent.yaml | kubectl apply -f -
envsubst < k8s-manifests/chat-gateway.yaml | kubectl apply -f -
envsubst < k8s-manifests/frontend-proxy.yaml | kubectl apply -f -

echo "⏳ Waiting for deployments..."
kubectl wait --for=condition=available --timeout=300s deployment/customer-service-agent
kubectl wait --for=condition=available --timeout=300s deployment/chat-gateway
kubectl wait --for=condition=available --timeout=300s deployment/frontend-proxy

echo "✅ Deployment complete!"
