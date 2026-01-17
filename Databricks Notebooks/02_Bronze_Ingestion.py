# Databricks notebook source
# MAGIC %run ./00_Common_Configs

# COMMAND ----------

# Cell 2: Read Raw Data
from pyspark.sql.functions import current_timestamp, input_file_name

# Read CSV with header
df_raw = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load(bronze_path+"/cybersecurity_attacks.csv")

# Display to verify
display(df_raw.limit(5))

# COMMAND ----------

# Cell 3: Transform & Write to Bronze Delta
df_bronze = df_raw.withColumn("ingestion_timestamp", current_timestamp()) \
                  .withColumn("source_file", input_file_name())

# Write to Data Lake (Bronze folder) as Delta
df_bronze.write.format("delta").mode("overwrite").save(bronze_path+"/delta/security_logs")

print(f"Bronze Delta Table written to: {bronze_path+'/delta/security_logs'}")

# COMMAND ----------

delta_bronze_path = bronze_path+"/delta/security_logs"

# COMMAND ----------

# Cell 4: Create SQL Table
spark.sql(f"CREATE TABLE IF NOT EXISTS security_logs_bronze USING DELTA LOCATION '{delta_bronze_path}' ")

# Verify we can query it with SQL
display(spark.sql("SELECT * FROM security_logs_bronze LIMIT 5"))

# COMMAND ----------

