#!/bin/bash
# deploy-k8s.sh - Kubernetes deployment script

set -e

echo "Deploying to Kubernetes..."

# Load environment
if [ -f .env ]; then
    source .env
fi

# Replace PROJECT_ID in manifests
for file in k8s/*.yaml; do
    sed -i.bak "s/PROJECT_ID/$PROJECT_ID/g" "$file"
done

# Create namespace and secrets
kubectl create namespace ai-agents --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic ai-secrets \
    --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY" \
    --namespace=ai-agents \
    --dry-run=client -o yaml | kubectl apply -f -

# Apply manifests
kubectl apply -f k8s/

# Wait for deployments
kubectl wait --for=condition=available deployment --all -n ai-agents --timeout=600s

echo "Kubernetes deployment complete!"