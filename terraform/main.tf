# 1. Configure the Azure Provider
# This tells Terraform we are talking to Azure (not AWS or Google).
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    databricks = {
      source = "databricks/databricks"
    }
  }
}

provider "azurerm" {
  features {}
}

provider "databricks" {
  host = azurerm_databricks_workspace.adb.workspace_url
}

# 2. Create a Resource Group
# The "folder" that holds everything.
resource "azurerm_resource_group" "rg" {
  name     = "rg-security-platform-dev"
  location = "Central US"
}

# 3. Create a Random String for Unique Names
# Azure Storage names must be globally unique. This generates a random suffix.
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# 4. Create the Data Lake (ADLS Gen2)
# We enable "is_hns_enabled" to turn it into a true Data Lake.
resource "azurerm_storage_account" "adls" {
  name                     = "sadatalake${random_string.suffix.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # Cheapest option
  is_hns_enabled           = true  # CRITICAL: Enables Hierarchical Namespace (Data Lake)
}

# 5. Create Containers (Bronze, Silver, Gold, Scripts)
# We use a loop (for_each) to avoid writing the same code 4 times.
resource "azurerm_storage_container" "containers" {
  for_each              = toset(["bronze", "silver", "gold", "scripts"])
  name                  = each.key
  storage_account_name  = azurerm_storage_account.adls.name
  container_access_type = "private"
}

# 6. Create Azure Databricks Workspace
# We choose "standard" sku to save money.
resource "azurerm_databricks_workspace" "adb" {
  name                = "adb-security-platform"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "standard" # Important for student budget
  depends_on = [azurerm_resource_group.rg]
}

# 7. Output the Storage Name
# This prints the name at the end so you know what was created.
output "storage_account_name" {
  value = azurerm_storage_account.adls.name
}