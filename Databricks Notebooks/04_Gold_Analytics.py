# Databricks notebook source
# MAGIC %run ./00_Common_Configs

# COMMAND ----------

from pyspark.sql.functions import udf, col
from pyspark.sql.types import LongType


# COMMAND ----------

df_silver = spark.read.table("security_logs_silver")

# COMMAND ----------

from pyspark.sql.functions import col, count, date_trunc, desc

df_hourly_trends = df_silver.groupBy(
    date_trunc("hour", col("event_time")).alias("hour_bucket"),
    col("threat_label")
).agg(count("*").alias("attack_count")).orderBy("hour_bucket")

df_top_ips = df_silver.groupBy("source_ip","country_name","threat_label") \
                      .agg(count("*").alias("total_attacks")) \
                      .orderBy(desc("total_attacks"))


# COMMAND ----------


gold_trends_path = f"{gold_path}/delta/hourly_trends"
df_hourly_trends.write.format("delta").mode("overwrite").save(gold_trends_path)
spark.sql(f"CREATE TABLE IF NOT EXISTS gold_hourly_trends USING DELTA LOCATION '{gold_trends_path}'")


gold_ips_path = f"{gold_path}/delta/top_ips"
df_top_ips.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(gold_ips_path)
spark.sql(f"CREATE TABLE IF NOT EXISTS gold_top_ips USING DELTA LOCATION '{gold_ips_path}'")

print("Gold Layer processing complete. Tables ready for Power BI.")

# COMMAND ----------

