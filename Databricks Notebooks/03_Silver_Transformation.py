# Databricks notebook source
# MAGIC %run ./00_Common_Configs

# COMMAND ----------

# MAGIC %pip install geoip2

# COMMAND ----------

from pyspark.sql import Row
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType
import geoip2.database
from pyspark.sql.functions import pandas_udf

import pandas as pd

spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")


file_path = f"abfss://bronze@{storage_account_name}.dfs.core.windows.net/GeoLite2-Country.mmdb"

MMDB_PATH = "/dbfs/FileStore/geolite/GeoLite2-Country.mmdb" 

dbutils.fs.cp(
    file_path,
    "dbfs:/FileStore/geolite/GeoLite2-Country.mmdb",
    True
)

out_schema = StructType([
    StructField("ip", StringType(), True),
    StructField("country_name", StringType(), True),
])

@pandas_udf(out_schema)
def ip_to_country(ip_series: pd.Series) -> pd.DataFrame:
    reader = geoip2.database.Reader(MMDB_PATH)
    try:
        iso_list = []
        name_list = []
        for ip in ip_series.astype(str):
            iso = name = None
            try:
                resp = reader.country(ip)
                name = resp.country.name
            except Exception:
                pass
            name_list.append(name)

        return pd.DataFrame({
            "ip": ip_series,
            "country_name": name_list
        })
    finally:
        reader.close()

# COMMAND ----------

# Cell 2: Read from Bronze Delta
bronze_path = f"abfss://bronze@{storage_account_name}.dfs.core.windows.net/delta/security_logs"
df_bronze = spark.read.format("delta").load(bronze_path)

display(df_bronze.limit(5))

# COMMAND ----------

# Cell 3: Clean and Transform
from pyspark.sql.functions import col, to_timestamp

# 1. Convert Timestamp string to actual Timestamp type
df_silver = df_bronze.withColumn("event_time", to_timestamp(col("Timestamp"), "yyyy-MM-dd HH:mm:ss")).dropDuplicates()


# COMMAND ----------

distinct_ips = df_silver.select(F.col("source_ip").alias("ip")).distinct()
geo_df = distinct_ips.select(ip_to_country(F.col("ip")).alias("g")).select("g.*")
final_df = df_silver.join(geo_df, df_silver.source_ip == geo_df.ip, "left").drop(geo_df["ip"])

# COMMAND ----------

# Cell 4: Write to Silver Container
silver_table_path = f"abfss://silver@{storage_account_name}.dfs.core.windows.net/delta/security_logs_silver"

final_df.write.format("delta").mode("overwrite").option("mergeSchema", "true").save(silver_table_path)

# Register as SQL Table
spark.sql(f"CREATE TABLE IF NOT EXISTS security_logs_silver USING DELTA LOCATION '{silver_table_path}'")

print("Silver Layer processing complete.")

# COMMAND ----------

