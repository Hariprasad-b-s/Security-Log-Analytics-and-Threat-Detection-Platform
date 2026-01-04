# jobs.tf

resource "databricks_job" "security_pipeline" {
  name = "Security-Log-ETL-Pipeline"

  # We define a "Job Cluster" spec here. 
  # It spins up ONLY when the job runs, then dies. Ideally cheaper than interactive.
  job_cluster {
    job_cluster_key = "job_cluster"
    new_cluster {
      node_type_id  = "Standard_D4s_v3"
      spark_version = "13.3.x-scala2.12"
      num_workers   = 0 # Single Node
      spark_conf = {
        "spark.databricks.cluster.profile" : "singleNode",
        "spark.master" : "local[*]"
      }
      custom_tags = {
        "ResourceClass" : "SingleNode"
      }
    }
  }

  # Task 1: Ingest Bronze
  task {
    task_key        = "ingest_bronze"
    job_cluster_key = "job_cluster"

    notebook_task {
      notebook_path = "/Production/02_Bronze_Ingestion"
      # NOTE: If your username in Databricks is your email, we might need to adjust the path above.
      # Ideally, we move notebooks to a shared folder, but let's try this first.
    }
  }

  # Task 2: Process Silver
  task {
    task_key        = "process_silver"
    job_cluster_key = "job_cluster"
    depends_on {
      task_key = "ingest_bronze"
    }

    notebook_task {
      notebook_path = "/Production/03_Silver_Transformation"
    }
  }

  # Task 3: Aggregate Gold
  task {
    task_key        = "analytics_gold"
    job_cluster_key = "job_cluster"
    depends_on {
      task_key = "process_silver"
    }

    notebook_task {
      notebook_path = "/Production/04_Gold_Analytics"
    }
  }
}
