terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.31"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

data "google_client_config" "default" {}

data "google_container_cluster" "sandbox" {
  name     = var.gke_cluster_name
  location = var.gcp_region
}

provider "kubernetes" {
  host                   = "https://${data.google_container_cluster.sandbox.endpoint}"
  token                  = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(data.google_container_cluster.sandbox.master_auth[0].cluster_ca_certificate)
}
