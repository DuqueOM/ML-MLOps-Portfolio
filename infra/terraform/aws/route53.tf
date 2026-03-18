# Route 53 — Custom Domain for ML Portfolio APIs
#
# Usage:
#   1. Register your domain via Route 53 or transfer an existing one.
#   2. Set var.domain_name in terraform.tfvars (e.g. "duqueom.dev").
#   3. Run: terraform plan -target=aws_route53_zone.portfolio
#            terraform apply -target=aws_route53_zone.portfolio
#   4. Update your domain registrar's NS records with the zone's nameservers (output below).
#   5. Run full: terraform apply
#
# Result:
#   api.<domain_name>/bankchurn/docs
#   api.<domain_name>/nlpinsight/docs
#   api.<domain_name>/chicagotaxi/docs

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------

variable "domain_name" {
  description = "Custom domain for the ML portfolio APIs (e.g. duqueom.dev). Leave empty to skip Route 53 setup."
  type        = string
  default     = ""
}

variable "enable_route53" {
  description = "Set to true to create Route 53 hosted zone and DNS records. Requires var.domain_name."
  type        = bool
  default     = false
}

# ---------------------------------------------------------------------------
# Data — NLB DNS + Zone ID (from the ingress-nginx LoadBalancer service)
# ---------------------------------------------------------------------------

data "aws_lb" "nlb" {
  count = var.enable_route53 ? 1 : 0

  tags = {
    "kubernetes.io/cluster/${var.project_name}-eks-${var.environment}" = "owned"
    "kubernetes.io/service-name"                                       = "ingress-nginx/ingress-nginx-controller"
  }
}

# ---------------------------------------------------------------------------
# Hosted Zone
# ---------------------------------------------------------------------------

resource "aws_route53_zone" "portfolio" {
  count = var.enable_route53 ? 1 : 0
  name  = var.domain_name

  tags = {
    Name        = "${var.project_name}-zone"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------------------------
# ALIAS record: api.<domain> → NLB DNS
# Using ALIAS (not CNAME) for apex/subdomain — no extra DNS hop, AWS-native
# ---------------------------------------------------------------------------

resource "aws_route53_record" "api" {
  count   = var.enable_route53 ? 1 : 0
  zone_id = aws_route53_zone.portfolio[0].zone_id
  name    = "api.${var.domain_name}"
  type    = "A"

  alias {
    name                   = data.aws_lb.nlb[0].dns_name
    zone_id                = data.aws_lb.nlb[0].zone_id
    evaluate_target_health = true
  }
}

# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

output "route53_name_servers" {
  description = "Nameservers to configure in your domain registrar (required for DNS delegation)"
  value       = var.enable_route53 ? aws_route53_zone.portfolio[0].name_servers : []
}

output "api_endpoint" {
  description = "Clean production API base URL"
  value       = var.enable_route53 ? "http://api.${var.domain_name}" : "http://${try(data.aws_lb.nlb[0].dns_name, "LoadBalancer not yet provisioned")}"
}

output "api_docs_urls" {
  description = "Swagger UI endpoints for all ML services"
  value = var.enable_route53 ? {
    bankchurn   = "http://api.${var.domain_name}/bankchurn/docs"
    nlpinsight  = "http://api.${var.domain_name}/nlpinsight/docs"
    chicagotaxi = "http://api.${var.domain_name}/chicagotaxi/docs"
    } : {
    bankchurn   = "http://${try(data.aws_lb.nlb[0].dns_name, "pending")}/bankchurn/docs"
    nlpinsight  = "http://${try(data.aws_lb.nlb[0].dns_name, "pending")}/nlpinsight/docs"
    chicagotaxi = "http://${try(data.aws_lb.nlb[0].dns_name, "pending")}/chicagotaxi/docs"
  }
}
