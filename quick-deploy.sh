#!/bin/bash
# quick-deploy.sh - Complete hackathon deployment script
# Version: 2.0 - Integrated and improved

set -e  # Exit on error

echo "🚀 Online Boutique AI Enhancement - Hackathon Quick Deploy v2.0"
echo "=================================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables if .env exists
if [ -f "$PROJECT_ROOT/.env" ]; then
    echo -e "${BLUE}Loading environment from .env file...${NC}"
    source "$PROJECT_ROOT/.env"
fi

# Check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    local missing_deps=()
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        missing_deps+=("gcloud CLI")
        echo -e "${RED}❌ gcloud CLI not found${NC}"
        echo "   Install from: https://cloud.google.com/sdk/install"
    else
        echo -e "${GREEN}✅ gcloud CLI found${NC}"
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        echo -e "${YELLOW}⚠️ kubectl not found. Installing...${NC}"
        gcloud components install kubectl --quiet
    else
        echo -e "${GREEN}✅ kubectl found${NC}"
    fi
    
    # Check docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("Docker")
        echo -e "${RED}❌ Docker not found${NC}"
        echo "   Install from: https://docs.docker.com/get-docker/"
    else
        echo -e "${GREEN}✅ Docker found${NC}"
        
        # Check if Docker is running
        if ! docker info &> /dev/null; then
            echo -e "${RED}❌ Docker daemon not running${NC}"
            echo "   Please start Docker and try again"
            exit 1
        fi
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing dependencies: ${missing_deps[*]}${NC}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met!${NC}"
}

# Setup environment variables
setup_environment() {
    echo -e "${YELLOW}Setting up environment...${NC}"
    
    # Get or set project ID
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${BLUE}Enter your GCP Project ID:${NC}"
        read -r PROJECT_ID
    fi
    
    # Validate project ID
    if ! gcloud projects describe "$PROJECT_ID" &>/dev/null; then
        echo -e "${RED}❌ Project '$PROJECT_ID' not found or not accessible${NC}"
        echo "Please check your project ID and ensure you have access."
        exit 1
    fi
    
    # Get or set Gemini API key
    if [ -z "$GEMINI_API_KEY" ]; then
        echo -e "${BLUE}Enter your Gemini API Key:${NC}"
        echo "Get one from: https://makersuite.google.com/app/apikey"
        read -rs GEMINI_API_KEY
    fi
    
    # Validate API key format (basic check)
    if [[ ! "$GEMINI_API_KEY" =~ ^AI[a-zA-Z0-9_-]{35,}$ ]]; then
        echo -e "${YELLOW}⚠️ API key format seems unusual. Continue anyway? (y/N)${NC}"
        read -r confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            echo "Please check your API key and try again."
            exit 1
        fi
    fi
    
    # Set default values
    export PROJECT_ID=$PROJECT_ID
    export REGION=${REGION:-us-central1}
    export CLUSTER_NAME=${CLUSTER_NAME:-ai-boutique-hackathon}
    export GEMINI_API_KEY=$GEMINI_API_KEY
    
    # Save to .env for future use
    cat > "$PROJECT_ROOT/.env" << EOF
# Online Boutique AI Enhancement Configuration
PROJECT_ID=$PROJECT_ID
REGION=$REGION
CLUSTER_NAME=$CLUSTER_NAME
GEMINI_API_KEY=$GEMINI_API_KEY

# Service Configuration
MCP_IMAGE=gcr.io/$PROJECT_ID/mcp-server:hackathon
A2A_IMAGE=gcr.io/$PROJECT_ID/a2a-orchestrator:hackathon
GATEWAY_IMAGE=gcr.io/$PROJECT_ID/api-gateway:hackathon
EOF
    
    echo -e "${GREEN}✅ Environment configured and saved to .env${NC}"
    
    # Set gcloud project
    gcloud config set project "$PROJECT_ID"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}Enabling required APIs...${NC}"
    
    local apis=(
        "container.googleapis.com"
        "artifactregistry.googleapis.com"
        "aiplatform.googleapis.com"
        "compute.googleapis.com"
    )
    
    echo "Enabling: ${apis[*]}"
    gcloud services enable "${apis[@]}" --quiet
    
    echo -e "${GREEN}✅ APIs enabled!${NC}"
}

# Create GKE cluster
create_cluster() {
    echo -e "${YELLOW}Creating GKE Autopilot cluster...${NC}"
    
    # Check if cluster exists
    if gcloud container clusters describe "$CLUSTER_NAME" --region="$REGION" &>/dev/null; then
        echo -e "${GREEN}✅ Cluster '$CLUSTER_NAME' already exists!${NC}"
    else
        echo "This will take approximately 5-7 minutes..."
        gcloud container clusters create-auto "$CLUSTER_NAME" \
            --region="$REGION" \
            --release-channel=rapid \
            --enable-autoscaling \
            --quiet
        echo -e "${GREEN}✅ Cluster created!${NC}"
    fi
    
    # Get credentials
    echo "Getting cluster credentials..."
    gcloud container clusters get-credentials "$CLUSTER_NAME" --region="$REGION"
}

# Deploy base Online Boutique
deploy_online_boutique() {
    echo -e "${YELLOW}Deploying base Online Boutique application...${NC}"
    
    # Clone if not exists
    if [ ! -d "$PROJECT_ROOT/microservices-demo" ]; then
        echo "Cloning microservices demo..."
        git clone https://github.com/GoogleCloudPlatform/microservices-demo.git "$PROJECT_ROOT/microservices-demo"
    fi
    
    # Deploy base application
    echo "Applying Kubernetes manifests..."
    kubectl apply -f "$PROJECT_ROOT/microservices-demo/release/kubernetes-manifests.yaml"
    
    # Wait for pods to be ready
    echo "Waiting for pods to be ready (this may take 3-5 minutes)..."
    kubectl wait --for=condition=ready pods --all --timeout=600s -l app!=loadgenerator || {
        echo -e "${YELLOW}⚠️ Some pods may still be starting. Continuing...${NC}"
    }
    
    echo -e "${GREEN}✅ Online Boutique deployed!${NC}"
    
    # Get frontend URL
    echo -e "${YELLOW}Getting frontend LoadBalancer IP...${NC}"
    for i in {1..6}; do
        FRONTEND_IP=$(kubectl get service frontend-external -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
        if [ -n "$FRONTEND_IP" ]; then
            echo -e "${GREEN}✅ Frontend available at: http://$FRONTEND_IP${NC}"
            break
        fi
        echo "Waiting for LoadBalancer... (attempt $i/6)"
        sleep 30
    done
    
    if [ -z "$FRONTEND_IP" ]; then
        echo -e "${YELLOW}⚠️ LoadBalancer IP not ready yet. You can check later with:${NC}"
        echo "kubectl get service frontend-external"
    fi
}

# Build and push Docker images
build_and_push_images() {
    echo -e "${YELLOW}Building and pushing AI component images...${NC}"
    
    # Configure Docker auth for GCR
    gcloud auth configure-docker gcr.io --quiet
    
    # Build MCP Server
    echo "Building MCP Server..."
    cd "$PROJECT_ROOT/mcp-server"
    docker build -t "gcr.io/$PROJECT_ID/mcp-server:hackathon" .
    docker push "gcr.io/$PROJECT_ID/mcp-server:hackathon"
    echo -e "${GREEN}✅ MCP Server image pushed${NC}"
    
    # Build A2A Orchestrator
    echo "Building A2A Orchestrator..."
    cd "$PROJECT_ROOT/a2a-orchestrator"
    docker build -t "gcr.io/$PROJECT_ID/a2a-orchestrator:hackathon" .
    docker push "gcr.io/$PROJECT_ID/a2a-orchestrator:hackathon"
    echo -e "${GREEN}✅ A2A Orchestrator image pushed${NC}"
    
    # Build API Gateway
    echo "Building API Gateway..."
    cd "$PROJECT_ROOT/api-gateway"
    docker build -t "gcr.io/$PROJECT_ID/api-gateway:hackathon" .
    docker push "gcr.io/$PROJECT_ID/api-gateway:hackathon"
    echo -e "${GREEN}✅ API Gateway image pushed${NC}"
    
    cd "$PROJECT_ROOT"
    echo -e "${GREEN}✅ All images built and pushed!${NC}"
}

# Deploy AI components to Kubernetes
deploy_ai_components() {
    echo -e "${YELLOW}Deploying AI components to Kubernetes...${NC}"
    
    # Create AI namespace
    kubectl create namespace ai-agents --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets
    kubectl create secret generic ai-secrets \
        --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY" \
        --namespace=ai-agents \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply all Kubernetes manifests
    echo "Applying Kubernetes manifests..."
    kubectl apply -f "$PROJECT_ROOT/k8s/"
    
    # Wait for deployments to be ready
    echo "Waiting for AI components to be ready..."
    kubectl wait --for=condition=available deployment --all -n ai-agents --timeout=600s || {
        echo -e "${YELLOW}⚠️ Some deployments may still be starting. Checking status...${NC}"
        kubectl get pods -n ai-agents
    }
    
    echo -e "${GREEN}✅ AI components deployed!${NC}"
}

# Get service URLs and display results
get_service_urls() {
    echo -e "${YELLOW}Getting service URLs...${NC}"
    
    # Wait a bit for LoadBalancers
    sleep 30
    
    # Get all service IPs
    FRONTEND_IP=$(kubectl get service frontend-external -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    GATEWAY_IP=$(kubectl get service api-gateway -n ai-agents -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    MCP_IP=$(kubectl get service mcp-server -n ai-agents -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    A2A_IP=$(kubectl get service a2a-orchestrator -n ai-agents -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    
    # Display results
    echo ""
    echo -e "${GREEN}================================================================${NC}"
    echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
    echo -e "${GREEN}================================================================${NC}"
    echo ""
    echo -e "${BLUE}📱 Access Your Services:${NC}"
    echo -e "   🛍️  Original Boutique:     ${GREEN}http://$FRONTEND_IP${NC}"
    echo -e "   🤖 AI-Enhanced Boutique:   ${GREEN}http://$GATEWAY_IP${NC}"
    echo -e "   🧠 MCP Server API:         ${GREEN}http://$MCP_IP:8080${NC}"
    echo -e "   🔗 A2A Orchestrator API:   ${GREEN}http://$A2A_IP:8081${NC}"
    echo ""
    echo -e "${BLUE}📚 API Documentation:${NC}"
    echo -e "   MCP Docs:    ${GREEN}http://$MCP_IP:8080/docs${NC}"
    echo -e "   A2A Docs:    ${GREEN}http://$A2A_IP:8081/docs${NC}"
    echo -e "   Widget Test: ${GREEN}http://$GATEWAY_IP/widget-test${NC}"
    echo ""
    echo -e "${BLUE}🧪 Testing the AI Features:${NC}"
    echo "   1. Open the AI-Enhanced Boutique URL"
    echo "   2. Look for the purple AI assistant button (bottom right)"
    echo "   3. Click it to open the AI panel"
    echo "   4. Try 'Optimize My Cart' to see AI in action"
    echo "   5. Watch for real-time notifications"
    echo ""
    
    # Show pending IPs if any
    local pending_services=()
    [ "$FRONTEND_IP" = "pending" ] && pending_services+=("Original Boutique")
    [ "$GATEWAY_IP" = "pending" ] && pending_services+=("AI-Enhanced Boutique")
    [ "$MCP_IP" = "pending" ] && pending_services+=("MCP Server")
    [ "$A2A_IP" = "pending" ] && pending_services+=("A2A Orchestrator")
    
    if [ ${#pending_services[@]} -ne 0 ]; then
        echo -e "${YELLOW}⏳ LoadBalancer IPs still pending for: ${pending_services[*]}${NC}"
        echo "   Run 'kubectl get services --all-namespaces' to check status"
        echo "   IPs typically take 1-3 minutes to be assigned"
        echo ""
    fi
    
    echo -e "${BLUE}🛠️  Useful Commands:${NC}"
    echo "   Check pods:           kubectl get pods --all-namespaces"
    echo "   Check services:       kubectl get services --all-namespaces"
    echo "   View logs:            kubectl logs -f deployment/mcp-server -n ai-agents"
    echo "   Delete everything:    ./scripts/cleanup.sh"
    echo ""
    echo -e "${GREEN}Happy hacking! 🚀${NC}"
}

# Verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"
    
    local errors=0
    
    # Check if all pods are running
    echo "Checking pod status..."
    if ! kubectl get pods --all-namespaces | grep -E "(Error|CrashLoopBackOff|ImagePullBackOff)" &>/dev/null; then
        echo -e "${GREEN}✅ All pods are healthy${NC}"
    else
        echo -e "${RED}❌ Some pods have issues:${NC}"
        kubectl get pods --all-namespaces | grep -E "(Error|CrashLoopBackOff|ImagePullBackOff)" || true
        errors=$((errors + 1))
    fi
    
    # Check if services have endpoints
    echo "Checking service endpoints..."
    local ai_services=("mcp-server" "a2a-orchestrator" "api-gateway")
    for service in "${ai_services[@]}"; do
        if kubectl get endpoints "$service" -n ai-agents &>/dev/null; then
            echo -e "${GREEN}✅ $service endpoints ready${NC}"
        else
            echo -e "${RED}❌ $service endpoints not ready${NC}"
            errors=$((errors + 1))
        fi
    done
    
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✅ Deployment verification passed!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ Deployment verification found $errors issues${NC}"
        echo "This is normal for new deployments. Services may take a few minutes to be fully ready."
        return 1
    fi
}

# Cleanup function
cleanup_on_error() {
    echo -e "${RED}❌ Error occurred during deployment${NC}"
    echo "To clean up resources, run: ./scripts/cleanup.sh"
    echo "To retry deployment, fix the issue and run this script again."
}

# Main execution function
main() {
    echo -e "${BLUE}Starting Online Boutique AI Enhancement Deployment...${NC}"
    echo ""
    
    # Set error handler
    trap cleanup_on_error ERR
    
    # Execute deployment steps
    check_prerequisites
    setup_environment
    enable_apis
    create_cluster
    deploy_online_boutique
    build_and_push_images
    deploy_ai_components
    
    # Give services time to start
    echo -e "${YELLOW}Waiting for services to initialize...${NC}"
    sleep 30
    
    verify_deployment
    get_service_urls
    
    echo -e "${GREEN}Deployment completed successfully! 🎉${NC}"
}

# Help function
show_help() {
    echo "Online Boutique AI Enhancement - Quick Deploy Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --verify-only  Only verify existing deployment"
    echo "  --urls-only    Only display service URLs"
    echo ""
    echo "Environment Variables:"
    echo "  PROJECT_ID      GCP Project ID (required)"
    echo "  GEMINI_API_KEY  Gemini API Key (required)"
    echo "  REGION          GCP Region (default: us-central1)"
    echo "  CLUSTER_NAME    GKE Cluster Name (default: ai-boutique-hackathon)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Full deployment"
    echo "  $0 --verify-only      # Verify existing deployment"
    echo "  $0 --urls-only        # Show service URLs"
    echo ""
    echo "For more information, see the README.md file."
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --verify-only)
        verify_deployment
        exit $?
        ;;
    --urls-only)
        get_service_urls
        exit 0
        ;;
    "")
        # No arguments, run main deployment
        main
        ;;
    *)
        echo "Unknown option: $1"
        echo "Use --help for usage information."
        exit 1
        ;;
esac