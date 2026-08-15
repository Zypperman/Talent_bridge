# Per-session isolation comes from Terraform workspaces (one per session_id),
# not separate backends — the default local backend already stores each
# workspace's state under terraform.tfstate.d/<workspace>/.
terraform {
  backend "local" {}
}
