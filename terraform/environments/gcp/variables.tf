variable "gcp_project_id" {
  description = "GCP project the sandbox GKE cluster lives in."
  type        = string
}

variable "gcp_region" {
  description = "Region of the GKE cluster. Defaults to Singapore, the closest region to Batam."
  type        = string
  default     = "asia-southeast1"
}

variable "gke_cluster_name" {
  description = "Name of the existing GKE Autopilot cluster sessions get provisioned into. This module does not create the cluster itself."
  type        = string
  default     = "talentbridge-sandbox"
}

variable "session_id" {
  description = "Sandbox session ID — also the Terraform workspace name."
  type        = string
}

variable "namespace" {
  description = "Namespace the session's mock topology was provisioned into."
  type        = string
}

variable "target" {
  description = "Value of the 'app' label on the pod(s) the fault targets."
  type        = string
}

variable "block_port" {
  description = "Port the fault represents as unreachable (see modules/fault_network_block)."
  type        = number
}
