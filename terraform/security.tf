# security.tf

# 1. Get Current Client Config 
# (This gets your "User ID" so Terraform can give you permission to the Vault)
data "azurerm_client_config" "current" {}

# 2. Create the Key Vault
resource "azurerm_key_vault" "kv" {
  name                        = "kv-security-logs-project"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false

  sku_name = "standard"

  # Access Policy: Give YOU (and Terraform) full control
  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Get",
    ]

    secret_permissions = [
      "Get", "List", "Set", "Delete", "Recover", "Backup", "Restore",
    ]

    storage_permissions = [
      "Get", "List"
    ]
  }

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    # This is the ID from your error message
    object_id          = "afa3138e-2429-4370-8e1b-b73dd6938159"
    secret_permissions = ["Get", "List"]
  }
}

# 3. Store the Storage Key as a Secret
# Terraform automatically grabs the key from the storage account we made earlier
resource "azurerm_key_vault_secret" "dl_key" {
  name         = "datalake-key"
  value        = azurerm_storage_account.adls.primary_access_key
  key_vault_id = azurerm_key_vault.kv.id
}

# 4. Output the Vault URI and ID
output "key_vault_uri" {
  value = azurerm_key_vault.kv.vault_uri
}

output "key_vault_id" {
  value = azurerm_key_vault.kv.id
}
