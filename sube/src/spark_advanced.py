# -*- coding: utf-8 -*-
"""PySpark高级任务：使用Spark MLlib复现TF-IDF和Word2Vec。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer, HashingTF, IDF, Word2Vec
from pyspark.sql.functions import col, udf, array, size
from pyspark.sql.types import ArrayType, StringType, FloatType
from pyspark.ml.linalg import Vectors
import jieba

HDFS_BASE = "/resume_matching"

def create_spark(app_name="SparkMLlibMatching"):
    return SparkSession.builder.appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.executor.memory", "2g").getOrCreate()

def jieba_cut(text):
    """UDF for jieba tokenization."""
    if not text:
        return []
    import jieba
    # Simple tokenization with basic stopword removal
    stop_words = {"的","了","和","是","就","都","而","及","与","着","或",
                  "一个","没有","我们","他们","自己","这","那","什么","怎么"}
    tokens = jieba.lcut(str(text))
    return [t.strip().lower() for t in tokens if len(t.strip()) >= 2 and t.strip() not in stop_words]

def main():
    spark = create_spark()
    print(f"[SPARK MLlib] Spark {spark.version}")

    # Read data
    base = os.path.dirname(os.path.dirname(__file__))
    r_path = "file:///" + os.path.join(base, "data", "resumes.csv").replace("\\", "/")
    j_path = "file:///" + os.path.join(base, "data", "jobs.csv").replace("\\", "/")

    df_r = spark.read.option("header","true").option("encoding","UTF-8").csv(r_path)
    df_j = spark.read.option("header","true").option("encoding","UTF-8").csv(j_path)

    # Build full text for tokenization
    from pyspark.sql.functions import concat_ws, coalesce, lit
    df_r = df_r.withColumn("full_text", concat_ws(" ", coalesce(col("skills"),lit("")), coalesce(col("project_experience"),lit("")), coalesce(col("self_description"),lit(""))))
    df_j = df_j.withColumn("full_text", concat_ws(" ", coalesce(col("job_title"),lit("")), coalesce(col("required_skills"),lit("")), coalesce(col("job_description"),lit(""))))

    # Tokenize (register UDF)
    spark.udf.register("jieba_cut_udf", jieba_cut, ArrayType(StringType()))
    df_r = df_r.withColumn("tokens", udf(jieba_cut, ArrayType(StringType()))("full_text"))
    df_j = df_j.withColumn("tokens", udf(jieba_cut, ArrayType(StringType()))("full_text"))

    # ---- Spark MLlib TF-IDF ----
    print("\n[SPARK MLlib] Computing TF-IDF...")
    all_texts = df_r.select("tokens").union(df_j.select("tokens"))
    hashingTF = HashingTF(inputCol="tokens", outputCol="rawFeatures", numFeatures=500)
    featurized = hashingTF.transform(all_texts)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    idf_model = idf.fit(featurized)
    tfidf_result = idf_model.transform(featurized)
    n_features = len(idf_model.idf)
    print(f"[SPARK MLlib] TF-IDF feature count: {n_features}")

    # ---- Spark MLlib Word2Vec ----
    print("\n[SPARK MLlib] Training Word2Vec...")
    w2v = Word2Vec(vectorSize=50, minCount=1, inputCol="tokens", outputCol="w2v_vector", seed=42)
    w2v_model = w2v.fit(all_texts)
    w2v_result = w2v_model.transform(all_texts)
    print(f"[SPARK MLlib] Word2Vec vocab size: {w2v_model.getVectors().count()}")

    # Show sample
    print("\n[SPARK MLlib] Sample results (TF-IDF):")
    tfidf_result.select("tokens", "features").show(3, truncate=80)
    print("\n[SPARK MLlib] Sample results (Word2Vec):")
    w2v_result.select("tokens", "w2v_vector").show(3, truncate=80)

    # Find similar words
    if w2v_model.getVectors().count() > 0:
        try:
            synonyms = w2v_model.findSynonyms("python", 5)
            print("\n[SPARK MLlib] Words similar to 'python':")
            synonyms.show()
        except Exception as e:
            print(f"[SPARK MLlib] No synonyms found: {e}")

    spark.stop()
    print("[SPARK MLlib] Job completed.")

if __name__ == "__main__":
    main()
