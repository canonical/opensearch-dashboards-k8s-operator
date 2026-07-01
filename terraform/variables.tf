# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "opensearch-dashboards"
}

variable "channel" {
  description = "Charm channel"
  type        = string
  default     = null
}

variable "base" {
  description = "Charm base"
  type        = string
  default     = "ubuntu@22.04"
}

variable "config" {
  description = "Map of charm configuration options"
  type        = map(string)
  default     = {}
}

variable "model_uuid" {
  description = "Model UUID"
  type        = string
}

variable "revision" {
  description = "Charm revision"
  type        = number
  default     = null
}

variable "units" {
  description = "Charm units"
  type        = number
  default     = 1
}

variable "constraints" {
  description = "String listing constraints for this application"
  type        = string
  default     = "arch=amd64"
}

variable "endpoint_bindings" {
  description = "Map of endpoint bindings"
  type        = map(string)
  default     = {}
}

variable "expose" {
  description = "Expose the application"
  type        = bool
  default     = false
}

variable "opensearch_offer_url" {
  description = "Offer URL of an opensearch application in a VM model (cross-model relation)"
  type        = string
  default     = null
}

variable "tls" {
  description = "Whether TLS should be enabled via self-signed-certificates"
  type        = bool
  default     = false
}

variable "self-signed-certificates" {
  description = "Configuration for the self-signed-certificates app"
  type = object({
    channel     = optional(string, "latest/stable")
    revision    = optional(number, null)
    base        = optional(string, "ubuntu@22.04")
    constraints = optional(string, "arch=amd64")
    config      = optional(map(string), { "ca-common-name" : "CA" })
  })
  default = {}
}
