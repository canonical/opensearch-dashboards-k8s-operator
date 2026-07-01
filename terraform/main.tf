# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

resource "juju_application" "opensearch-dashboards" {

  charm {
    name     = "opensearch-dashboards-k8s"
    channel  = var.channel
    revision = var.revision
    base     = var.base
  }
  config      = var.config
  model_uuid  = var.model_uuid
  name        = var.app_name
  units       = var.units
  constraints = var.constraints

  dynamic "expose" {
    for_each = var.expose ? [1] : []
    content {}
  }

  endpoint_bindings = [
    for k, v in var.endpoint_bindings : {
      endpoint = k, space = v
    }
  ]
}

# Deploy self-signed-certificates in the k8s model if tls enabled
resource "juju_application" "self-signed-certificates" {
  for_each = var.tls ? { "deployed" = true } : {}

  model_uuid = var.model_uuid

  charm {
    name     = "self-signed-certificates"
    channel  = var.self-signed-certificates.channel
    revision = var.self-signed-certificates.revision
    base     = var.self-signed-certificates.base
  }
  constraints = var.self-signed-certificates.constraints
  config      = var.self-signed-certificates.config
}

resource "juju_integration" "tls-opensearch_dashboards_integration" {
  for_each = var.tls ? { "deployed" = true } : {}

  model_uuid = var.model_uuid

  application {
    name = juju_application.self-signed-certificates["deployed"].name
  }

  application {
    name     = juju_application.opensearch-dashboards.name
    endpoint = "certificates"
  }

  depends_on = [
    juju_application.opensearch-dashboards,
    juju_application.self-signed-certificates,
  ]
}
