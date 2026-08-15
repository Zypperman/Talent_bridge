variable "kubeconfig_path" {
  description = "Path to the kubeconfig for the local sandbox cluster. Overridable via TF_VAR_kubeconfig_path (set by services/sandbox_service/terraform_runner.py from SANDBOX_KUBECONFIG)."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_context" {
  description = "kubeconfig context for the local sandbox cluster. Overridable via TF_VAR_kube_context (set from SANDBOX_KUBE_CONTEXT)."
  type        = string
  default     = "kind-talentbridge-sandbox"
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
