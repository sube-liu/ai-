# -*- coding: utf-8 -*-
"""
第2步：数据探索
对原始脏数据进行全面探索，生成数据探索报告。
"""
import pandas as pd
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "workflow", "01_ai_generate_dirty_data", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def explore_data():
    resumes_path = os.path.join(INPUT_DIR, "raw_resumes_dirty.csv")
    jobs_path = os.path.join(INPUT_DIR, "raw_jobs_dirty.csv")

    if not os.path.exists(resumes_path) or not os.path.exists(jobs_path):
        print("[ERROR] Input files not found. Run Step 1 first.")
        sys.exit(1)

    df_r = pd.read_csv(resumes_path, encoding="utf-8-sig")
    df_j = pd.read_csv(jobs_path, encoding="utf-8-sig")

    report_lines = []
    def log(msg):
        print(msg)
        report_lines.append(msg)

    log("=" * 60)
    log("DATA EXPLORATION REPORT")
    log("=" * 60)

    # ---- 1. Scale ----
    log("\n--- 1. Data Scale ---")
    log(f"Resumes: {df_r.shape[0]} rows, {df_r.shape[1]} columns")
    log(f"Jobs:    {df_j.shape[0]} rows, {df_j.shape[1]} columns")

    # ---- 2. Field names ----
    log("\n--- 2. Resume Fields ---")
    log(str(df_r.columns.tolist()))
    log("\n--- 2. Job Fields ---")
    log(str(df_j.columns.tolist()))

    # ---- 3. First few rows ----
    log("\n--- 3. Resumes First 5 Rows ---")
    log(df_r.head(5).to_string())
    log("\n--- 3. Jobs First 5 Rows ---")
    log(df_j.head(5).to_string())

    # ---- 4. dtypes ----
    log("\n--- 4. Resume dtypes ---")
    log(str(df_r.dtypes))
    log("\n--- 4. Job dtypes ---")
    log(str(df_j.dtypes))

    # ---- 5. Missing values ----
    log("\n--- 5. Missing Values (Resumes) ---")
    missing_r = df_r.isnull().sum()
    log(str(missing_r[missing_r > 0]))

    log("\n--- 5. Missing Values (Jobs) ---")
    missing_j = df_j.isnull().sum()
    log(str(missing_j[missing_j > 0]))

    # Also check for empty strings
    log("\n--- 5b. Empty Strings (Resumes) ---")
    for col in df_r.columns:
        empty_count = (df_r[col] == "").sum()
        if empty_count > 0:
            log(f"  {col}: {empty_count} empty values")

    log("\n--- 5b. Empty Strings (Jobs) ---")
    for col in df_j.columns:
        empty_count = (df_j[col] == "").sum()
        if empty_count > 0:
            log(f"  {col}: {empty_count} empty values")

    # ---- 6. Duplicates ----
    log("\n--- 6. Duplicates ---")
    log(f"Resume duplicates: {df_r.duplicated().sum()}")
    log(f"Job duplicates:    {df_j.duplicated().sum()}")

    # ---- 7. Unique value analysis ----
    log("\n--- 7. Education Distribution ---")
    log(str(df_r["education"].value_counts(dropna=False)))

    log("\n--- 7. City Distribution (Resumes) ---")
    log(str(df_r["city"].value_counts(dropna=False)))

    log("\n--- 7. City Distribution (Jobs) ---")
    log(str(df_j["city"].value_counts(dropna=False)))

    # ---- 8. Skills analysis ----
    log("\n--- 8. Skills Field Issues ---")
    for idx, row in df_r.iterrows():
        skills = str(row["skills"])
        if not skills.strip():
            log(f"  {row['resume_id']}: skills field is EMPTY")
        elif ";;" in skills:
            log(f"  {row['resume_id']}: double separator found -> {skills}")
        elif skills.count(";") == 0:
            log(f"  {row['resume_id']}: no semicolon separator -> {skills}")

    for idx, row in df_j.iterrows():
        skills = str(row["required_skills"])
        if not skills.strip():
            log(f"  {row['job_id']}: required_skills field is EMPTY")

    # ---- 9. Experience analysis ----
    log("\n--- 9. Experience Years Distribution (Resumes) ---")
    log(str(df_r["experience_years"].describe()))

    log("\n--- 9. Min Experience Distribution (Jobs) ---")
    log(str(df_j["min_experience_years"].describe()))

    # ---- 10. Text field lengths ----
    log("\n--- 10. Text Field Length Stats ---")
    df_r["desc_len"] = df_r["self_description"].fillna("").apply(len)
    df_r["proj_len"] = df_r["project_experience"].fillna("").apply(len)
    log(f"resume self_description length: min={df_r['desc_len'].min()}, max={df_r['desc_len'].max()}, mean={df_r['desc_len'].mean():.1f}")
    log(f"resume project_experience length: min={df_r['proj_len'].min()}, max={df_r['proj_len'].max()}, mean={df_r['proj_len'].mean():.1f}")

    df_j["jd_len"] = df_j["job_description"].fillna("").apply(len)
    log(f"job job_description length: min={df_j['jd_len'].min()}, max={df_j['jd_len'].max()}, mean={df_j['jd_len'].mean():.1f}")

    # ---- 11. Salary ranges ----
    log("\n--- 11. Salary Ranges ---")
    log(f"Resume expected_salary: min={df_r['expected_salary'].min()}, max={df_r['expected_salary'].max()}, mean={df_r['expected_salary'].mean():.1f}")
    log(f"Job salary: min={df_j['salary'].min()}, max={df_j['salary'].max()}, mean={df_j['salary'].mean():.1f}")

    # ---- Save report ----
    report_md = "\n".join(report_lines)
    report_path = os.path.join(OUTPUT_DIR, "data_exploration_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Data Exploration Report\n\n")
        f.write("```text\n")
        f.write(report_md)
        f.write("\n```\n")
    print(f"\n[OK] Report saved to: {report_path}")
    return df_r, df_j

if __name__ == "__main__":
    explore_data()
