# -*- coding: utf-8 -*-
"""PySpark version of the resume-job matching pipeline.

This script covers the improvement points in the local workflow:
- Spark DataFrame based data loading and rule scoring.
- Spark MLlib Tokenizer, HashingTF, IDF and Word2Vec for semantic features.
- Optional HDFS input/output paths, with local file paths as the default.

Run locally:
    spark-submit src/spark_match_pipeline.py

Run with HDFS:
    spark-submit src/spark_match_pipeline.py \
        --resumes hdfs:///resume_matching/raw_data/resumes.csv \
        --jobs hdfs:///resume_matching/raw_data/jobs.csv \
        --output hdfs:///resume_matching/results/match_results
"""
from __future__ import annotations

import argparse
import math
import os
from typing import Iterable

from pyspark.ml.feature import HashingTF, IDF, Tokenizer, Word2Vec
from pyspark.ml.linalg import SparseVector, VectorUDT
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    array_intersect,
    array_except,
    coalesce,
    col,
    concat_ws,
    greatest,
    least,
    lit,
    lower,
    regexp_replace,
    round as spark_round,
    size,
    split,
    trim,
    udf,
    when,
)
from pyspark.sql.types import DoubleType


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

WEIGHTS = {
    "skill_score": 0.30,
    "tfidf_score": 0.20,
    "word2vec_score": 0.15,
    "education_score": 0.15,
    "experience_score": 0.10,
    "city_score": 0.05,
    "certificate_score": 0.05,
}

EDU_LEVEL = {
    "高中": 1,
    "大专": 2,
    "本科": 3,
    "硕士": 4,
    "博士": 5,
}


def create_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("ResumeJobSparkMatching")
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def local_csv(name: str) -> str:
    return "file:///" + os.path.join(BASE_DIR, "data", name).replace("\\", "/")


def normalize_items(column_name: str):
    cleaned = lower(regexp_replace(coalesce(col(column_name), lit("")), r"[，,、/|]", ";"))
    return split(cleaned, r"\s*;\s*")


def optional_col(df: DataFrame, preferred: str, fallback: str, default: str = ""):
    """Use a column when present, otherwise fall back without breaking raw CSV input."""
    if preferred in df.columns:
        return col(preferred)
    if fallback in df.columns:
        return col(fallback)
    return lit(default)


def read_csv(spark: SparkSession, path: str) -> DataFrame:
    return (
        spark.read.option("header", "true")
        .option("inferSchema", "true")
        .option("encoding", "UTF-8")
        .csv(path)
    )


def prepare_resumes(df: DataFrame) -> DataFrame:
    text = concat_ws(
        " ",
        coalesce(col("skills"), lit("")),
        coalesce(col("major"), lit("")),
        coalesce(col("project_experience"), lit("")),
        coalesce(col("self_description"), lit("")),
    )
    return (
        df.dropDuplicates(["resume_id"])
        .withColumn("resume_education", col("education"))
        .withColumn("resume_skills", normalize_items("skills"))
        .withColumn("resume_certs", normalize_items("certificates"))
        .withColumn("resume_text", text)
        .withColumn("resume_city", optional_col(df, "city_normalized", "city"))
        .withColumn("resume_exp", coalesce(col("experience_years").cast("double"), lit(0.0)))
        .withColumn("expected_salary_num", coalesce(col("expected_salary").cast("double"), lit(0.0)))
    )


def prepare_jobs(df: DataFrame) -> DataFrame:
    text = concat_ws(
        " ",
        coalesce(col("job_title"), lit("")),
        coalesce(col("required_skills"), lit("")),
        coalesce(col("job_description"), lit("")),
    )
    return (
        df.dropDuplicates(["job_id"])
        .withColumn("job_skills", normalize_items("required_skills"))
        .withColumn("job_certs", normalize_items("preferred_certificates"))
        .withColumn("job_text", text)
        .withColumn("job_city", optional_col(df, "city_normalized", "city"))
        .withColumn("job_exp", coalesce(col("min_experience_years").cast("double"), lit(0.0)))
        .withColumn("salary_num", coalesce(col("salary").cast("double"), lit(0.0)))
    )


def cosine(a, b) -> float:
    if a is None or b is None:
        return 0.0
    a_vals = a.toArray() if isinstance(a, SparseVector) else list(a)
    b_vals = b.toArray() if isinstance(b, SparseVector) else list(b)
    dot = float(sum(x * y for x, y in zip(a_vals, b_vals)))
    na = math.sqrt(sum(x * x for x in a_vals))
    nb = math.sqrt(sum(y * y for y in b_vals))
    if na == 0 or nb == 0:
        return 0.0
    return max(0.0, min(100.0, dot / (na * nb) * 100.0))


cosine_udf = udf(cosine, DoubleType())


def semantic_features(resumes: DataFrame, jobs: DataFrame) -> tuple[DataFrame, DataFrame]:
    resume_text = resumes.select(
        col("resume_id").alias("entity_id"),
        lit("resume").alias("entity_type"),
        col("resume_text").alias("text"),
    )
    job_text = jobs.select(
        col("job_id").alias("entity_id"),
        lit("job").alias("entity_type"),
        col("job_text").alias("text"),
    )
    corpus = resume_text.unionByName(job_text).fillna({"text": ""})

    tokenizer = Tokenizer(inputCol="text", outputCol="tokens")
    tokens = tokenizer.transform(corpus)

    hashing_tf = HashingTF(inputCol="tokens", outputCol="raw_features", numFeatures=1024)
    featurized = hashing_tf.transform(tokens)
    idf_model = IDF(inputCol="raw_features", outputCol="tfidf_features").fit(featurized)
    tfidf = idf_model.transform(featurized)

    word2vec = Word2Vec(
        vectorSize=50,
        minCount=1,
        inputCol="tokens",
        outputCol="w2v_features",
        seed=42,
    )
    w2v = word2vec.fit(tokens).transform(tfidf)

    resume_features = (
        w2v.filter(col("entity_type") == "resume")
        .select(
            col("entity_id").alias("resume_id"),
            col("tfidf_features").alias("resume_tfidf"),
            col("w2v_features").alias("resume_w2v"),
        )
    )
    job_features = (
        w2v.filter(col("entity_type") == "job")
        .select(
            col("entity_id").alias("job_id"),
            col("tfidf_features").alias("job_tfidf"),
            col("w2v_features").alias("job_w2v"),
        )
    )
    return resume_features, job_features


def add_rule_scores(pairs: DataFrame) -> DataFrame:
    matched = array_intersect(col("resume_skills"), col("job_skills"))
    missing = array_except(col("job_skills"), col("resume_skills"))
    skill_score = when(size(col("job_skills")) <= 0, lit(100.0)).otherwise(
        size(matched) / greatest(size(col("job_skills")), lit(1)) * 100.0
    )

    edu_score = when(col("resume_edu_level") >= col("job_edu_level"), 100.0).when(
        col("resume_edu_level") == col("job_edu_level") - 1, 50.0
    ).otherwise(0.0)

    exp_score = when(col("resume_exp") >= col("job_exp"), 100.0).when(
        col("resume_exp") >= col("job_exp") - 1, 50.0
    ).otherwise(0.0)

    city_score = when(trim(col("resume_city")) == trim(col("job_city")), 100.0).otherwise(0.0)

    cert_score = when(size(col("job_certs")) <= 0, 100.0).otherwise(
        size(array_intersect(col("resume_certs"), col("job_certs")))
        / greatest(size(col("job_certs")), lit(1))
        * 100.0
    )

    return (
        pairs.withColumn("matched_array", matched)
        .withColumn("missing_array", missing)
        .withColumn("skill_score", spark_round(skill_score, 1))
        .withColumn("education_score", edu_score)
        .withColumn("experience_score", exp_score)
        .withColumn("city_score", city_score)
        .withColumn("certificate_score", spark_round(cert_score, 1))
        .withColumn("matched_skills", concat_ws(";", col("matched_array")))
        .withColumn("missing_skills", concat_ws(";", col("missing_array")))
    )


def with_education_levels(df: DataFrame, src_col: str, out_col: str) -> DataFrame:
    expr = lit(3)
    for label, level in EDU_LEVEL.items():
        expr = when(col(src_col) == label, lit(level)).otherwise(expr)
    return df.withColumn(out_col, expr)


def build_matches(resumes: DataFrame, jobs: DataFrame) -> DataFrame:
    resumes = with_education_levels(resumes, "education", "resume_edu_level")
    jobs = with_education_levels(jobs, "required_education", "job_edu_level")
    resume_features, job_features = semantic_features(resumes, jobs)

    pairs = (
        resumes.join(resume_features, "resume_id")
        .crossJoin(jobs.join(job_features, "job_id"))
        .withColumn("tfidf_score", spark_round(cosine_udf(col("resume_tfidf"), col("job_tfidf")), 1))
        .withColumn("word2vec_score", spark_round(cosine_udf(col("resume_w2v"), col("job_w2v")), 1))
    )
    scored = add_rule_scores(pairs)

    total = lit(0.0)
    for col_name, weight in WEIGHTS.items():
        total = total + col(col_name) * lit(weight)

    return (
        scored.withColumn("total_score", spark_round(total, 1))
        .withColumn(
            "reason",
            concat_ws(
                "；",
                concat_ws("", lit("共同技能："), col("matched_skills")),
                concat_ws("", lit("缺少技能："), col("missing_skills")),
            ),
        )
        .select(
            "resume_id",
            "name",
            "job_id",
            "job_title",
            "company",
            "resume_education",
            "skill_score",
            "tfidf_score",
            "word2vec_score",
            "education_score",
            "experience_score",
            "city_score",
            "certificate_score",
            "matched_skills",
            "missing_skills",
            "total_score",
            "reason",
        )
        .orderBy(col("total_score").desc())
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resumes", default=local_csv("resumes.csv"))
    parser.add_argument("--jobs", default=local_csv("jobs.csv"))
    parser.add_argument(
        "--output",
        default="file:///" + os.path.join(BASE_DIR, "workflow", "11_build_match_results", "outputs", "spark_match_results").replace("\\", "/"),
    )
    args = parser.parse_args()

    spark = create_spark()
    resumes = prepare_resumes(read_csv(spark, args.resumes))
    jobs = prepare_jobs(read_csv(spark, args.jobs))

    matches = build_matches(resumes, jobs)
    matches.coalesce(1).write.mode("overwrite").option("header", "true").option("encoding", "UTF-8").csv(args.output)
    print(f"[OK] Spark match results written to {args.output}")
    spark.stop()


if __name__ == "__main__":
    main()
