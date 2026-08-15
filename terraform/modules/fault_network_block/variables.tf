variable "namespace" {
  description = "Namespace the sandbox session's mock topology was provisioned into."
  type        = string
}

variable "session_id" {
  description = "Sandbox session this fault belongs to; used to name the resource uniquely."
  type        = string
}

variable "target" {
  description = "Value of the 'app' label on the pod(s) to cut off from the network."
  type        = string
}

variable "block_port" {
  description = "Port the fault is meant to represent as unreachable. Recorded as an annotation for evidence/logging — the policy itself denies all ingress to the target, see main.tf."
  type        = number
}
