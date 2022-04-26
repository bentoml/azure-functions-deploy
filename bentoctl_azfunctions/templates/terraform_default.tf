# main.tf 

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
}

################################################################################
# Input variable definitions
################################################################################

variable "deployment_name" {
  type = string
}

variable "resource_group" {
  type = string
}

variable "acr_name" {
  type = string
}

variable "image_tag" {
    type = string
}

variable "image_repository" {
  type = string
}

variable "image_version" {
  type = string
}

variable "max_burst" {
    type = number
}

variable "min_instances" {
    type = number
}

variable "premium_plan_sku" {
    type = string
}


################################################################################
# Resource definitions
################################################################################

data "azurerm_resource_group" "rg" {
  name = var.resource_group
}

data "azurerm_container_registry" "registry" {
  name                = var.acr_name
  resource_group_name = data.azurerm_resource_group.rg.name
}

resource "random_id" "storage_account" {
  byte_length = 8
}

resource "azurerm_storage_account" "storage" {
  name                     = "storage${lower(random_id.storage_account.hex)}"
  resource_group_name      = data.azurerm_resource_group.rg.name
  location                 = data.azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_application_insights" "application_insights" {
  name                = "${var.deployment_name}-application-insights"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  application_type    = "other"
}


resource "azurerm_app_service_plan" "plan" {
  name                = "${var.deployment_name}-premiumPlan"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "PremiumV2"
    size = var.premium_plan_sku
  }
}



resource "azurerm_function_app" "funcApp" {
  name                       = "${var.deployment_name}-${lower(random_id.storage_account.hex)}"
  location                   = data.azurerm_resource_group.rg.location
  resource_group_name        = data.azurerm_resource_group.rg.name
  app_service_plan_id        = azurerm_app_service_plan.plan.id
  storage_account_name       = azurerm_storage_account.storage.name
  storage_account_access_key = azurerm_storage_account.storage.primary_access_key
  version                    = "~3"
  os_type = "linux"

  app_settings = {
    FUNCTION_APP_EDIT_MODE              = "readOnly"
    https_only                          = true
    FUNCTIONS_EXTENSION_VERSION         = "~3"
    DOCKER_REGISTRY_SERVER_URL          = "${data.azurerm_container_registry.registry.login_server}"
    DOCKER_REGISTRY_SERVER_USERNAME     = "${data.azurerm_container_registry.registry.admin_username}"
    DOCKER_REGISTRY_SERVER_PASSWORD     = "${data.azurerm_container_registry.registry.admin_password}"
    WEBSITES_ENABLE_APP_SERVICE_STORAGE = false
    APPINSIGHTS_INSTRUMENTATIONKEY      = azurerm_application_insights.application_insights.instrumentation_key
  }

  site_config {
    always_on        = true
    linux_fx_version = "DOCKER|${data.azurerm_container_registry.registry.login_server}/${var.image_repository}:${var.image_version}"
    elastic_instance_minimum = var.min_instances
    app_scale_limit = var.max_burst
  }

  depends_on = [azurerm_storage_account.storage, azurerm_app_service_plan.plan]
}
################################################################################
# Output value definitions
################################################################################
output url {
  description = "Base URL for API Gateway stage."
  value       = azurerm_function_app.funcApp.default_hostname
}

output image {
    description = "The image deployed."
    value = var.image_tag
}
