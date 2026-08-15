module "fault" {
  source     = "../../modules/fault_network_block"
  namespace  = var.namespace
  session_id = var.session_id
  target     = var.target
  block_port = var.block_port
}
