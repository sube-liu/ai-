# -*- coding: utf-8 -*-
"""
第3步：数据清洗
修复脏数据中的问题：空值填充、去除首尾空格、去重、修正技能分隔符。
"""
import pandas as pd
import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "workflow", "01_ai_generate_dirty_data", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_data():
    resumes_path = os.path.join(INPUT_DIR, "raw_resumes_dirty.csv")
    jobs_path = os.path.join(INPUT_DIR, "raw_jobs_dirty.csv")

    df_r = pd.read_csv(resumes_path, encoding="utf-8-sig")
    df_j = pd.read_csv(jobs_path, encoding="utf-8-sig")

    log_lines = []
    def log(msg):
        print(msg)
        log_lines.append(msg)

    log("=" * 50)
    log("CLEANING LOG")
    log("=" * 50)

    # ---- 1. Strip whitespace ----
    log("\n[1] Stripping whitespace from all string columns...")
    for col in df_r.columns:
        if df_r[col].dtype == object:
            df_r[col] = df_r[col].astype(str).str.strip()
    for col in df_j.columns:
        if df_j[col].dtype == object:
            df_j[col] = df_j[col].astype(str).str.strip()

    # ---- 2. Convert "nan" string to empty ----
    df_r.replace("nan", "", inplace=True)
    df_j.replace("nan", "", inplace=True)

    # ---- 3. Handle empty education (R010) ----
    log("\n[2] Filling empty education fields...")
    empty_edu = (df_r["education"] == "") | (df_r["education"].isna())
    log(f"  Resumes with empty education: {empty_edu.sum()}")
    # Fill with "本科" as reasonable default for CS students
    df_r.loc[empty_edu, "education"] = "本科"
    log("  -> Filled with '本科'")

    # ---- 4. Fix skill separators ----
    log("\n[3] Fixing skill separator issues...")
    def fix_skills(val):
        if not val.strip():
            return val
        # Remove double semicolons
        val = re.sub(r";;+", ";", val)
        # Split, strip each, rejoin
        parts = [p.strip() for p in val.split(";") if p.strip()]
        return ";".join(parts)

    df_r["skills"] = df_r["skills"].apply(fix_skills)
    df_j["required_skills"] = df_j["required_skills"].apply(fix_skills)

    # ---- 5. Handle empty skills (R018) ----
    empty_skills_r = (df_r["skills"] == "")
    if empty_skills_r.any():
        log(f"\n[5] Resumes with empty skills: {empty_skills_r.sum()}")
        log("  Skipping (will handle during matching)")

    # ---- 6. Fill empty city ----
    log("\n[6] Filling empty city fields...")
    empty_city = (df_r["city"] == "")
    log(f"  Resumes with empty city: {empty_city.sum()}")
    if empty_city.any():
        # Use most common city or "未知"
        most_common = df_r["city"].value_counts().index[0]
        if most_common == "":
            most_common = "南昌"
        df_r.loc[empty_city, "city"] = most_common
        log(f"  -> Filled with '{most_common}'")

    # ---- 7. Fill empty company (J012) ----
    empty_company = (df_j["company"] == "")
    log(f"\n[7] Jobs with empty company: {empty_company.sum()}")
    if empty_company.any():
        df_j.loc[empty_company, "company"] = "未知公司"
        log("  -> Filled with '未知公司'")

    # ---- 8. Fill empty job_description (J012) ----
    empty_jd = (df_j["job_description"] == "")
    log(f"\n[8] Jobs with empty job_description: {empty_jd.sum()}")
    if empty_jd.any():
        # Use job_title as fallback
        df_j.loc[empty_jd, "job_description"] = df_j.loc[empty_jd, "job_title"].apply(lambda x: f"负责{x}相关工作")
        log("  -> Filled with job-title based fallback")

    # ---- 9. Fix certificate format ----
    log("\n[9] Standardizing certificate formats...")
    cert_map = {"四级": "英语四级", "二级": "计算机二级"}
    df_r["certificates"] = df_r["certificates"].fillna("")
    def fix_certs(val):
        if not isinstance(val, str) or not val.strip():
            return ""
        parts = [p.strip() for p in val.split(";") if p.strip()]
        fixed = []
        for p in parts:
            fixed.append(cert_map.get(p, p))
        return ";".join(fixed)
    df_r["certificates"] = df_r["certificates"].apply(fix_certs)

    # ---- 10. Drop duplicates ----
    log("\n[10] Checking duplicates...")
    r_dup = df_r.duplicated()
    j_dup = df_j.duplicated()
    log(f"  Resume duplicates: {r_dup.sum()}")
    log(f"  Job duplicates: {j_dup.sum()}")
    if r_dup.any():
        df_r = df_r[~r_dup]
        log("  -> Removed resume duplicates")
    if j_dup.any():
        df_j = df_j[~j_dup]
        log("  -> Removed job duplicates")

    # ---- Save ----
    clean_r_path = os.path.join(OUTPUT_DIR, "clean_resumes.csv")
    clean_j_path = os.path.join(OUTPUT_DIR, "clean_jobs.csv")
    df_r.to_csv(clean_r_path, index=False, encoding="utf-8-sig")
    df_j.to_csv(clean_j_path, index=False, encoding="utf-8-sig")

    log_path = os.path.join(OUTPUT_DIR, "cleaning_log.md")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("# Cleaning Log\n\n```text\n")
        f.write("\n".join(log_lines))
        f.write("\n```\n")

    log(f"\n[OK] Clean resumes saved: {clean_r_path} ({len(df_r)} rows)")
    log(f"[OK] Clean jobs saved:    {clean_j_path} ({len(df_j)} rows)")
    log(f"[OK] Cleaning log saved:  {log_path}")

if __name__ == "__main__":
    clean_data()
