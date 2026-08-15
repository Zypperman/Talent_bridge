# Sandbox Terraform

Two root modules, one shared fault module — see [docs/Sandbox_Architecture.md](../docs/Sandbox_Architecture.md) for the full design.

```text
terraform/
├── modules/
│   └── fault_network_block/   # Cuts a mock component off the network — the actual "trigger the incident" step
└── environments/
    ├── local/                 # kind/Minikube — kubernetes provider only, local state
    └── gcp/                   # GKE Autopilot — google + kubernetes providers, GCS backend
```

Both environments expose the same variables (`session_id`, `namespace`, `target`, `block_port`), so `services/sandbox_service/terraform_runner.py` can drive either one without knowing which it's talking to — it just points `SANDBOX_TF_ENV` at `local` or `gcp`.

## Local

```bash
# one-time: create the cluster sessions get provisioned into
kind create cluster --name talentbridge-sandbox

cd terraform/environments/local
terraform init
terraform workspace new <session-id>
terraform apply -var session_id=<session-id> -var namespace=<namespace> -var target=storage-array -var block_port=3260
```

## GCP

```bash
cd terraform/environments/gcp
terraform init -backend-config="bucket=<your-state-bucket>"
terraform workspace new <session-id>
terraform apply \
  -var gcp_project_id=<project> \
  -var session_id=<session-id> -var namespace=<namespace> \
  -var target=storage-array -var block_port=3260
```

The GCP root module reads the GKE cluster via `data "google_container_cluster"` — it expects a cluster named by `gke_cluster_name` (default `talentbridge-sandbox`) to already exist in `gcp_region`. It doesn't create the cluster itself.
