# cluster.tf

# Create a Single Node Databricks Cluster
# We use specific Spark settings to enforce "Single Node" mode (Zero workers).
resource "databricks_cluster" "singlenode" {
  cluster_name            = "single-node-cluster"
  node_type_id            = "Standard_D4s_v3"  # 7GB RAM, 2 Cores
  spark_version           = "13.3.x-scala2.12" # LTS Version
  autotermination_minutes = 20                 # Auto-off after 20 mins to save $$$

  # CONFIGURATION FOR SINGLE NODE (Zero Workers)
  spark_conf = {
    "spark.databricks.cluster.profile" : "singleNode",
    "spark.master" : "local[*]"
  }

  custom_tags = {
    "ResourceClass" : "SingleNode"
  }

  num_workers = 0 # Crucial: Must be 0 for single node
}
