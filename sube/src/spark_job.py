# -*- coding: utf-8 -*-
"""PySpark任务：从HDFS读取数据、清洗、写回HDFS。"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, when, regexp_replace, length
import os, sys

HDFS_BASE = "/resume_matching"

def create_spark(app_name="ResumeMatchingSparkJob"):
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def read_csv_from_hdfs(spark, path):
    """从HDFS读取CSV文件。"""
    print(f"[SPARK] Reading from HDFS: {path}")
    df = spark.read.option("header", "true").option("inferSchema", "true") \
        .option("encoding", "UTF-8").csv(path)
    print(f"[SPARK] Read {df.count()} rows, {len(df.columns)} columns")
    return df

def clean_with_spark(df, name):
    """使用PySpark进行数据清洗。"""
    print(f"[SPARK] Cleaning {name}...")
    # Trim whitespace from string columns
    for c in df.columns:
        if df.schema[c].dataType.typeName() == "string":
            df = df.withColumn(c, trim(col(c)))
    # Remove rows where key fields are all null
    if "skills" in df.columns:
        df = df.filter(col("skills").isNotNull() & (length(col("skills")) > 0))
    if "required_skills" in df.columns:
        df = df.filter(col("required_skills").isNotNull() & (length(col("required_skills")) > 0))
    # Drop duplicates
    before = df.count()
    df = df.dropDuplicates()
    after = df.count()
    print(f"[SPARK] {name}: {before} -> {after} rows (removed {before - after} duplicates)")
    df.printSchema()
    return df

def write_to_hdfs(df, path):
    """将DataFrame写入HDFS（CSV格式）。"""
    print(f"[SPARK] Writing to HDFS: {path}")
    df.coalesce(1).write.mode("overwrite").option("header", "true").option("encoding", "UTF-8").csv(path)
    print(f"[SPARK] Written successfully to {path}")

def main():
    spark = create_spark()
    print(f"[SPARK] Spark version: {spark.version}")
    print(f"[SPARK] Master: {spark.sparkContext.master}")

    # Read raw data from HDFS
    resumes_path = f"{HDFS_BASE}/raw_data/resumes.csv"
    jobs_path = f"{HDFS_BASE}/raw_data/jobs.csv"
    # Fallback to local if HDFS not available
    if not resumes_path.startswith("hdfs://"):
        print("[SPARK] Trying local data as fallback...")
        resumes_path = "file:///" + os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "resumes.csv").replace("\\", "/")
        jobs_path = "file:///" + os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "jobs.csv").replace("\\", "/")

    df_r = read_csv_from_hdfs(spark, resumes_path)
    df_j = read_csv_from_hdfs(spark, jobs_path)

    # Clean
    df_r_clean = clean_with_spark(df_r, "resumes")
    df_j_clean = clean_with_spark(df_j, "jobs")

    # Write results
    out_r = f"{HDFS_BASE}/cleaned_data/cleaned_resumes"
    out_j = f"{HDFS_BASE}/cleaned_data/cleaned_jobs"
    try:
        write_to_hdfs(df_r_clean, out_r)
        write_to_hdfs(df_j_clean, out_j)
    except Exception as e:
        print(f"[SPARK] HDFS write failed, saving locally: {e}")
        local_out = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(local_out, exist_ok=True)
        df_r_clean.coalesce(1).write.mode("overwrite").option("header","true").csv(local_out + "/cleaned_resumes")
        df_j_clean.coalesce(1).write.mode("overwrite").option("header","true").csv(local_out + "/cleaned_jobs")
        print(f"[SPARK] Local output saved to {local_out}")

    spark.stop()
    print("[SPARK] Job completed.")

if __name__ == "__main__":
    main()
