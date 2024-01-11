terraform {
  required_providers {
    kind = {
      source = "tehcyx/kind"
      version = "0.0.15"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.7.0"
    }
    helm = {
      source = "hashicorp/helm"
      version = "2.9.0"
    }
  }
}

provider "kind" {}

provider "helm"{
  kubernetes {
    config_path = "~/.kube/config"

  }
}
resource "kind_cluster" "default" {
  name = "kind-tf"
  node_image = "kindest/node:v1.23.4"
  wait_for_ready = true
  kind_config {
    kind = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"
    }

    node {
      role = "worker"
      kubeadm_config_patches = [
      <<-EOF
        kind: JoinConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "node=worker_1"
        extraMounts:
          - hostPath: ./data
            containerPath: /tmp/data
      EOF
      ]
    }

    node {
      role = "worker"
      kubeadm_config_patches = [
      <<-EOF
        kind: JoinConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "node=worker_2"
        extraMounts:
          - hostPath: ./data
            containerPath: /tmp/data
      EOF
      ]
    }
    node {
      role = "worker"
      kubeadm_config_patches = [
      <<-EOF
        kind: JoinConfiguration
        nodeRegistration:
          kubeletExtraArgs:
            node-labels: "node=worker_3"
        extraMounts:
          - hostPath: ./data
            containerPath: /tmp/data
      EOF
      ]
    }
  }
}

provider "kubernetes" {
  host = "${kind_cluster.default.endpoint}"
  cluster_ca_certificate = "${kind_cluster.default.cluster_ca_certificate}"
  client_certificate = "${kind_cluster.default.client_certificate}"
  client_key = "${kind_cluster.default.client_key}"
}

resource "kubernetes_namespace" "airflow-ns" {
  metadata {
    name = "airflow"
  }
}


resource "kubernetes_persistent_volume" "pv_airflow_logs" {
  depends_on = [kubernetes_namespace.airflow-ns]
  metadata {
    name = "pv-airflow-logs"
  }

  spec {
    capacity = {
      storage = "2Gi"
    }
    storage_class_name = "manual"
    access_modes = ["ReadWriteMany"]

    persistent_volume_source {
      host_path {
        path = "/tmp/data"
      }
    }
  }
  }

resource "kubernetes_persistent_volume_claim" "pvc_airflow_logs" {

  depends_on = [kubernetes_persistent_volume.pv_airflow_logs]
  metadata {
    name = "pvc-airflow-logs"
    namespace = "airflow"
  }

  spec {
    access_modes = ["ReadWriteMany"]
    resources {

      requests = {
        storage = "2Gi"
      }
    }
    storage_class_name = "manual"
    #volume_name = "${kubernetes_persistent_volume.pv_airflow_logs.metadata.0.name}"
  }
}

resource "helm_release" "airflow" {
  depends_on = [kubernetes_namespace.airflow-ns]
  name       = "airflow"
  chart      = "apache-airflow/airflow"
  version    = "1.11.0"
  namespace  = "airflow"
  repository = " https://airflow.apache.org"
  wait       = false
  #https://github.com/hashicorp/terraform-provider-helm/issues/683
  #repository = "https://airflow-helm.github.io/charts"

  values = [
    "${file("./values.yaml")}"
  ]

}
