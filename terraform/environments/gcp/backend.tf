terraform {
  backend "gcs" {
    # Bucket is intentionally not hardcoded here — pass it at init time so the
    # same config works across environments/projects:
    #   terraform init -backend-config="bucket=<your-state-bucket>"
    prefix = "sandbox/fault-state"
  }
}
