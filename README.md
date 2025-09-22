# kubestronautinmaking-GKE10
kubestronautinmaking-GKE10

╔════════════════════════════════════════════════════════════════╗
║      Steps to integrate the Ai-Agents                          ║
╚════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════╗
║                Architecture                                    ║
╚════════════════════════════════════════════════════════════════╝

AI-Enhanced Online Boutique - Production Architecture

![Alt text](./project_architecture.jpg)


===============================================================

┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐     ┌────────────────┐
│    Users    │────▶│Load Balancer │────▶│   Frontend Proxy    │────▶│   Original     │
│ (Internet)  │     │   (GCP LB)   │     │   (AI Gateway)      │     │   Frontend     │
└─────────────┘     └──────────────┘     │ • Widget Injection  │     │   (React)      │
                                         │ • API Routing       │     └────────────────┘
                                         └─────────┬───────────┘
                                                   │ /api/ai-chat
                                                   ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           AI Enhancement Layer                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│ ┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   │
│ │ Chat Gateway  │──▶│ Customer Service│──▶│ Personal Shopper│   │ Order Manager   │   │
│ │ (Load Balance)│   │     Agent       │   │     Agent       │   │     Agent       │   │
│ │ Port: 80      │   │ • Intent Class. │   │ • Product AI    │   │ • Tracking AI   │   │
│ └───────────────┘   │ • Query Routing │   │ • Recommends    │   │ • Status Update │   │
│                     └─────────┬───────┘   └─────────────────┘   └─────────────────┘   │
│                               │                     ▲                     ▲           │
│                               ▼                     │                     │           │
│ ┌───────────────┐   ┌─────────────────┐           ┌─────────────────────────────┐     │
│ │  A2A Network  │◄──│  MCP Servers    │           │      Agent Communication   │     │
│ │ (WebSocket)   │   │ • Product MCP   │           │      (WebSocket/HTTP)       │     │
│ │ • Agent Comm  │   │ • Order MCP     │           └─────────────────────────────┘     │
│ └───────────────┘   │ • Data Bridge   │                                               │
│                     └─────────┬───────┘                                               │
└─────────────────────────────────┼─────────────────────────────────────────────────────┘
                                  │ gRPC Bridge
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                      Original Online Boutique Microservices                             │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│ │  Product    │ │    Cart     │ │  Checkout   │ │  Payment    │ │  Shipping   │         │
│ │  Catalog    │ │  Service    │ │  Service    │ │  Service    │ │  Service    │         │
│ │ Port: 3550  │ │ Port: 7070  │ │ Port: 5050  │ │ Port: 50051 │ │ Port: 50051 │         │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                                                         │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐         │
│ │  Currency   │ │Recommendation│ │   Email     │ │     Ad      │ │ Redis Cache │        │
│ │  Service    │ │   Service    │ │  Service    │ │  Service    │ │ (Session)   │        │
│ │ Port: 7000  │ │ Port: 8080   │ │ Port: 8080  │ │ Port: 9555  │ │ Port: 6379  │        │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘         │
│                                                                                         │
│                            All Services: gRPC Communication                             │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    Google Kubernetes Engine (Autopilot)                                │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│ ┌─────────────────────────────────┐     ┌─────────────────────────────────┐             │
│ │         Node Pool 1             │     │         Node Pool 2             │             │
│ │    (Original Services)          │     │       (AI Services)             │             │
│ │                                 │     │                                 │             │
│ │                                 │     │                                 │             │
│ │ • ProductCatalog                │     │ • Chat Gateway                  │             │
│ │ • Cart Service                  │     │ • Customer Service Agent        │             │
│ │ • Checkout Service              │     │ • Personal Shopper Agent        │             │
│ │ • Payment Service               │     │ • Order Manager Agent           │             │
│ │ • Shipping Service              │     │ • A2A Network                   │             │
│ │ • Currency Service              │     │ • MCP Servers                   │             │
│ │ • Recommendation Service        │     │ • Frontend Proxy                │             │
│ │ • Email Service                 │     │                                 │             │
│ │ • Ad Service                    │     │                                 │             │
│ │ • Redis Cache                   │     │                                 │             │
│ │ • Original Frontend             │     │                                 │             │
│ └─────────────────────────────────┘     └─────────────────────────────────┘             │
│                                                                                         │
│ ┌─────────────────────────────────────────────────────────────────────────────────┐     │
│ │                          Auto-scaling Features                                  │     │
│ │ • Horizontal Pod Autoscaler (HPA)                                               │     │
│ │ • Vertical Pod Autoscaler (VPA)                                                 │     │
│ │ • Cluster Autoscaler                                                            │     │
│ │ • Resource Requests: ~300m CPU, ~1Gi Memory                                     │     │
│ │ • Load Balancer Services for External Access                                    │     │
│ └─────────────────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Data Flow:
==========
1. User ──HTTP──▶ Load Balancer ──▶ Frontend Proxy
2. Frontend Proxy ──▶ Original Frontend (Normal Traffic)
3. Frontend Proxy ──/api/ai-chat──▶ Chat Gateway ──▶ Customer Service Agent
4. Customer Service Agent ──Intent Classification──▶ Specialized AI Agents
5. AI Agents ──MCP Protocol──▶ MCP Servers ──gRPC──▶ Microservices
6. Response ──▶ AI Agents ──▶ Chat Gateway ──▶ Frontend Proxy ──▶ User

Communication Protocols:
========================
┌─────────────────┬─────────────────┬──────────────────────┐
│    Component    │    Protocol     │       Purpose        │
├─────────────────┼─────────────────┼──────────────────────┤
│ User ↔ Frontend │      HTTP       │   Web Interface      │
│ Frontend ↔ AI   │   HTTP/REST     │   API Calls          │
│ AI Agents       │   WebSocket     │ Agent Communication  │
│ MCP ↔ Services  │     gRPC        │ Microservice Access  │
│ Internal Mesh   │   HTTP/gRPC     │ Service Mesh         │
└─────────────────┴─────────────────┴──────────────────────┘

Technology Stack:
=================
• Frontend: React/HTML + AI Widget Injection
• AI Agents: Python FastAPI + Google Gemini
• Original Services: Go/Java/C# + gRPC
• Communication: gRPC + WebSocket + HTTP REST
• Data Storage: Redis Cache + Ephemeral
• Infrastructure: GKE Autopilot + Docker Containers
• Load Balancing: Google Cloud Load Balancer
• Monitoring: Kubernetes Health Checks + Logging

Key Features:
=============
✅ Non-invasive AI Enhancement (No Core Code Changes)
✅ Real-time Product Search & Intelligent Recommendations  
✅ Multi-Agent Conversation Handling with Intent Classification
✅ Order Tracking & Cart Management Integration
✅ Production-Ready Scalability & Auto-scaling
✅ Fault-Tolerant with Service Health Monitoring
✅ Secure Service Mesh Communication
✅ Resource-Optimized Deployment



╔════════════════════════════════════════════════════════════════╗
║      Terraform to build the kubernetes cluster.                ║
╚════════════════════════════════════════════════════════════════╝

<!-- Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->

# Use Terraform to deploy Online Boutique on a GKE cluster

This page walks you through the steps required to deploy the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) sample application on a [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) cluster using Terraform.

## Prerequisites

1. [Create a new project or use an existing project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#console) on Google Cloud, and ensure [billing is enabled](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled) on the project.

## Deploy the sample application

1. Clone the Github repository.

    ```bash
    git clone https://github.com/GoogleCloudPlatform/microservices-demo.git
    ```

1. Move into the `terraform/` directory which contains the Terraform installation scripts.

    ```bash
    cd microservices-demo/terraform
    ```

Set the Google Cloud project and region and ensure the Google Kubernetes Engine API is enabled.
```
export PROJECT_ID=<PROJECT_ID>
export REGION=us-central1
gcloud services enable container.googleapis.com \
  --project=${PROJECT_ID}
  ```

  1. gcloud auth login
1. gcloud config set project kubestronautinmaking
2. gcloud auth application-default login

1. Open the `terraform.tfvars` file and replace `<project_id_here>` with the [GCP Project ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects?hl=en#identifying_projects) for the `gcp_project_id` variable.

1. (Optional) If you want to provision a [Google Cloud Memorystore (Redis)](https://cloud.google.com/memorystore) instance, you can change the value of `memorystore = false` to `memorystore = true` in this `terraform.tfvars` file.

1. Initialize Terraform.

    ```bash
    terraform init
    ```

1. See what resources will be created.

    ```bash
    terraform plan
    ```

1. Create the resources and deploy the sample.

    ```bash
    terraform apply
    ```

    1. If there is a confirmation prompt, type `yes` and hit Enter/Return.

    Note: This step can take about 10 minutes. Do not interrupt the process.

Once the Terraform script has finished, you can locate the frontend's external IP address to access the sample application.

- Option 1:

    ```bash
    kubectl get service frontend-external | awk '{print $4}'
    ```

- Option 2: On Google Cloud Console, navigate to "Kubernetes Engine" and then "Services & Ingress" to locate the Endpoint associated with "frontend-external".

## Clean up

To avoid incurring charges to your Google Cloud account for the resources used in this sample application, either delete the project that contains the resources, or keep the project and delete the individual resources.

To remove the individual resources created for by Terraform without deleting the project:

1. Navigate to the `terraform/` directory.

1. Set `deletion_protection` to `false` for the `google_container_cluster` resource (GKE cluster).

   ```bash
   # Uncomment the line: "deletion_protection = false"
   sed -i "s/# deletion_protection/deletion_protection/g" main.tf

   # Re-apply the Terraform to update the state
   terraform apply
   ```

1. Run the following command:

   ```bash
   terraform destroy
   ```

   1. If there is a confirmation prompt, type `yes` and hit Enter/Return.



╔════════════════════════════════════════════════════════════════╗
║      Steps to build the Ai-Agents                              ║
╚════════════════════════════════════════════════════════════════╝
AI-Enhanced Online Boutique Deployment

This document provides scripts and instructions to deploy the AI-Enhanced Online Boutique on Google Kubernetes Engine (GKE).

Environment and Frontend Setup
1. 1. Set environment variables
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export CLUSTER_NAME="ai-boutique-hackathon"
export GEMINI_API_KEY="your-gemini-api-key"

2. 2. Set project
gcloud config set project $PROJECT_ID

3. 3. Enable required APIs
gcloud services enable \
   container.googleapis.com \
   artifactregistry.googleapis.com \
   aiplatform.googleapis.com \
   compute.googleapis.com

4. 4. Create GKE cluster
./boutique-ai-platform/deploy.sh

5. 5. Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION


Deployment Options
Before running scripts:

chmod +x boutique-ai-platform/deploy.sh

Monitoring & Debugging
Check service status

kubectl get services --all-namespaces
kubectl get service api-gateway -n ai-agents
kubectl get service frontend-external

Check pod status

kubectl get pods --all-namespaces

View logs

kubectl logs deployment/mcp-server -n ai-agents -f
kubectl logs deployment/a2a-orchestrator -n ai-agents -f
kubectl logs deployment/api-gateway -n ai-agents -f

Cleanup
manually delete the namespace:

kubectl delete namespace ai-agents


╔════════════════════════════════════════════════════════════════╗
║                Resources                                       ║
╚════════════════════════════════════════════════════════════════╝

Demo Application without AI:
Demo Application with AI:

Video recording of the demo:
Artical published and its url:
