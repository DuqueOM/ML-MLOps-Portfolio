# =============================================================================
# OPA/Conftest Policies for Kubernetes Manifests
# MLOps Portfolio — Production Security & Best Practices
# Usage: conftest test k8s/ -p tests/infra/kubernetes/policies/
# =============================================================================
package main

import future.keywords.in

# ---------------------------------------------------------------------------
# DENY: Containers must not run as root
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.securityContext.runAsNonRoot
    not input.spec.template.spec.securityContext.runAsNonRoot
    msg := sprintf("Deployment '%s': container '%s' should set securityContext.runAsNonRoot=true", [input.metadata.name, container.name])
}

# ---------------------------------------------------------------------------
# DENY: Containers must have resource limits
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.limits
    msg := sprintf("Deployment '%s': container '%s' missing resource limits", [input.metadata.name, container.name])
}

# ---------------------------------------------------------------------------
# DENY: Containers must have resource requests
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.requests
    msg := sprintf("Deployment '%s': container '%s' missing resource requests", [input.metadata.name, container.name])
}

# ---------------------------------------------------------------------------
# DENY: Containers must have liveness probes
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.livenessProbe
    msg := sprintf("Deployment '%s': container '%s' missing livenessProbe", [input.metadata.name, container.name])
}

# ---------------------------------------------------------------------------
# DENY: Containers must have readiness probes
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.readinessProbe
    msg := sprintf("Deployment '%s': container '%s' missing readinessProbe", [input.metadata.name, container.name])
}

# ---------------------------------------------------------------------------
# WARN: Images should not use :latest tag in production
# ---------------------------------------------------------------------------
warn[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    endswith(container.image, ":latest")
    msg := sprintf("Deployment '%s': container '%s' uses :latest tag — pin to specific version for production", [input.metadata.name, container.name])
}

# ---------------------------------------------------------------------------
# DENY: All resources must have namespace set
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind in ["Deployment", "Service", "ConfigMap", "HorizontalPodAutoscaler"]
    not input.metadata.namespace
    msg := sprintf("%s '%s': must specify namespace", [input.kind, input.metadata.name])
}

# ---------------------------------------------------------------------------
# DENY: Deployments must have app label
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "Deployment"
    not input.metadata.labels.app
    msg := sprintf("Deployment '%s': missing 'app' label", [input.metadata.name])
}

# ---------------------------------------------------------------------------
# WARN: CPU limits should be set to prevent resource starvation
# ---------------------------------------------------------------------------
warn[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    container.resources.limits
    not container.resources.limits.cpu
    msg := sprintf("Deployment '%s': container '%s' has memory limit but no CPU limit", [input.metadata.name, container.name])
}

# ---------------------------------------------------------------------------
# DENY: Services should not use LoadBalancer type (use Ingress instead)
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    msg := sprintf("Service '%s': avoid LoadBalancer type — use Ingress for external access", [input.metadata.name])
}

# ---------------------------------------------------------------------------
# WARN: HPA should have scaleDown stabilization to prevent flapping
# ---------------------------------------------------------------------------
warn[msg] {
    input.kind == "HorizontalPodAutoscaler"
    not input.spec.behavior.scaleDown.stabilizationWindowSeconds
    msg := sprintf("HPA '%s': missing scaleDown stabilizationWindowSeconds", [input.metadata.name])
}

# ---------------------------------------------------------------------------
# DENY: Namespace must have ResourceQuota
# ---------------------------------------------------------------------------
deny[msg] {
    input.kind == "ResourceQuota"
    not input.spec.hard["requests.cpu"]
    msg := sprintf("ResourceQuota '%s': must define requests.cpu", [input.metadata.name])
}

# ---------------------------------------------------------------------------
# WARN: Init containers should have resource limits too
# ---------------------------------------------------------------------------
warn[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.initContainers[_]
    not container.resources
    msg := sprintf("Deployment '%s': init container '%s' missing resource limits", [input.metadata.name, container.name])
}
