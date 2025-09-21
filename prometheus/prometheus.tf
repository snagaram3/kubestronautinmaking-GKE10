# main.tf - Prometheus and Grafana deployment on existing GKE cluster

# Configure Kubernetes provider to use existing GKE cluster
provider "kubernetes" {
  # Assumes you have kubectl configured to point to your GKE cluster
  # Alternatively, you can configure this to use GKE cluster credentials
}

provider "helm" {
  kubernetes {
    # Same configuration as kubernetes provider
  }
}

# Create monitoring namespace
resource "kubernetes_namespace" "monitoring" {
  metadata {
    name = "monitoring"
  }
}

# Deploy Prometheus using Helm
resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = kubernetes_namespace.monitoring.metadata[0].name
  version    = "51.2.0"

  set {
    name  = "prometheus.service.type"
    value = "ClusterIP"
  }

  set {
    name  = "grafana.service.type"
    value = "ClusterIP"
  }

  set {
    name  = "alertmanager.service.type"
    value = "ClusterIP"
  }

  # Enable persistence for Prometheus
  set {
    name  = "prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage"
    value = "10Gi"
  }

  # Enable persistence for Grafana
  set {
    name  = "grafana.persistence.enabled"
    value = "true"
  }

  set {
    name  = "grafana.persistence.size"
    value = "5Gi"
  }

  # Set Grafana admin password
  set {
    name  = "grafana.adminPassword"
    value = "admin123"
  }

  # Enable ServiceMonitor for microservices discovery
  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  # Configure scrape configs for microservices
  values = [
    <<EOF
prometheus:
  prometheusSpec:
    additionalScrapeConfigs:
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name

grafana:
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: 'default'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/default
  
  dashboards:
    default:
      kubernetes-cluster:
        gnetId: 315
        revision: 3
        datasource: Prometheus
      kubernetes-pods:
        gnetId: 6417
        revision: 1
        datasource: Prometheus
      node-exporter:
        gnetId: 1860
        revision: 27
        datasource: Prometheus
EOF
  ]

  timeout = 600
}

# Create ServiceMonitor for microservices (example)
resource "kubernetes_manifest" "microservice_monitor" {
  manifest = {
    apiVersion = "monitoring.coreos.com/v1"
    kind       = "ServiceMonitor"
    metadata = {
      name      = "microservices-monitor"
      namespace = kubernetes_namespace.monitoring.metadata[0].name
      labels = {
        app = "microservices-monitor"
      }
    }
    spec = {
      selector = {
        matchLabels = {
          monitoring = "enabled"
        }
      }
      endpoints = [
        {
          port     = "metrics"
          interval = "30s"
          path     = "/metrics"
        }
      ]
      namespaceSelector = {
        matchNames = ["default", "microservices"] # Add your microservices namespaces
      }
    }
  }

  depends_on = [helm_release.prometheus]
}

# Output connection information
output "prometheus_port_forward_command" {
  description = "Command to port-forward to Prometheus"
  value       = "kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
}

output "grafana_port_forward_command" {
  description = "Command to port-forward to Grafana"
  value       = "kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80"
}

output "grafana_credentials" {
  description = "Grafana login credentials"
  value = {
    username = "admin"
    password = "admin123"
  }
  sensitive = true
}

output "prometheus_url" {
  description = "Prometheus URL after port-forwarding"
  value       = "http://localhost:9090"
}

output "grafana_url" {
  description = "Grafana URL after port-forwarding"
  value       = "http://localhost:3000"
}