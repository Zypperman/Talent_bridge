# Build context is the repo root (see docker-compose.yml) so this can pull in
# common/, charts/, and terraform/ alongside its own code.
FROM python:3.11-slim

ARG TERRAFORM_VERSION=1.9.8
ARG KUBECTL_VERSION=v1.31.0
ARG HELM_VERSION=v3.16.2

# terraform/kubectl/helm are shelled out to by k8s_runner.py and
# terraform_runner.py — this service can't provision anything without them.
RUN apt-get update && apt-get install -y --no-install-recommends curl unzip ca-certificates && \
    curl -fsSL -o /tmp/terraform.zip "https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip" && \
    unzip -o /tmp/terraform.zip -d /usr/local/bin && rm /tmp/terraform.zip && \
    curl -fsSL -o /usr/local/bin/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    chmod +x /usr/local/bin/kubectl && \
    curl -fsSL -o /tmp/helm.tar.gz "https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz" && \
    tar -xzf /tmp/helm.tar.gz -C /tmp && mv /tmp/linux-amd64/helm /usr/local/bin/helm && rm -rf /tmp/helm.tar.gz /tmp/linux-amd64 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

COPY services/sandbox_service/requirements.txt services/sandbox_service/requirements.txt
RUN pip install --no-cache-dir -r services/sandbox_service/requirements.txt

COPY common common
COPY services/sandbox_service services/sandbox_service
COPY charts charts
COPY terraform terraform

CMD ["python", "services/sandbox_service/worker.py"]
