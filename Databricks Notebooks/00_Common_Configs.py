# Databricks notebook source
# 00_Common_Config
# This notebook sets up the global environment.
# Run this at the start of every other notebook.

# 1. Fetch Secret
scope_name = "security-secrets"
secret_key = "datalake-key"

storage_account_name = "sadatalake85s5r7" 

try:
    access_key = dbutils.secrets.get(scope = scope_name, key = secret_key)
except:
    print("Error: Could not find secret. Check Scope name.")

# 2. Set Spark Config
spark.conf.set(
    f"fs.azure.account.key.{storage_account_name}.dfs.core.windows.net",
    access_key
)

# 3. Define Standard Paths (Variables)

bronze_path = f"abfss://bronze@{storage_account_name}.dfs.core.windows.net"
silver_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net"
gold_path   = f"abfss://gold@{storage_account_name}.dfs.core.windows.net"

print(f"Global Configuration Loaded. Storage: {storage_account_name}")

# COMMAND ----------

