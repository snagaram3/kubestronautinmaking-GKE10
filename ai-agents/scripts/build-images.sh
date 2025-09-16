#!/bin/bash
# build-images.sh - Docker image building script

set -e

echo "Building Docker images..."

# Load environment
if [ -f .env ]; then
    source .env
fi

# Configure Docker auth
gcloud auth configure-docker gcr.io --quiet

# Build and push each component
for component in mcp-server a2a-orchestrator api-gateway; do
    echo "Building $component..."
    cd $component
    docker build -t gcr.io/$PROJECT_ID/$component:hackathon .
    docker push gcr.io/$PROJECT_ID/$component:hackathon
    cd ..
done

echo "All images built and pushed!"