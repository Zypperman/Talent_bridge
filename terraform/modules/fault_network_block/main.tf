# Simulates a mock data-center component going unreachable (e.g. "storage
# array down") by denying all ingress traffic to pods matching the target
# label. A real fault is rarely a clean single-port outage, and a topology
# this small doesn't need per-port fidelity to be a useful exercise — so
# this cuts the component off entirely rather than modeling partial failure.
resource "kubernetes_network_policy_v1" "block" {
  metadata {
    name      = "sandbox-fault-${var.session_id}"
    namespace = var.namespace
    annotations = {
      "talentbridge.io/represents-port" = tostring(var.block_port)
      "talentbridge.io/session-id"      = var.session_id
    }
  }

  spec {
    pod_selector {
      match_labels = {
        app = var.target
      }
    }

    policy_types = ["Ingress"]
    # No ingress rule below -> default-deny for pods matched by pod_selector.
  }
}
