output "network_policy_name" {
  value = kubernetes_network_policy_v1.block.metadata[0].name
}
