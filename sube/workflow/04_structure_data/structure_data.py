# -*- coding: utf-8 -*-
"""
第4步：字段结构化
学历等级映射、经验年数数值化、城市标准化、薪资标准化、技能/证书列表切分。
"""
import pandas as pd
import os
import sys
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "workflow", "03_clean_data", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---- 学历等级映射 ----
EDUCATION_LEVEL = {
    "博士": 5, "硕士": 4, "本科": 3, "大专": 2, "高中": 1, "": 0
}

# ---- 城市标准化映射（部分城市列表） ----
CITY_MAP = {
    "南昌": "南昌", "北京": "北京", "上海": "上海", "深圳": "深圳",
    "广州": "广州", "杭州": "杭州", "成都": "成都", "武汉": "武汉",
    "南京": "南京", "厦门": "厦门", "": "未知"
}

def structure_data():
    resumes_path = os.path.join(INPUT_DIR, "clean_resumes.csv")
    jobs_path = os.path.join(INPUT_DIR, "clean_jobs.csv")

    if not os.path.exists(resumes_path):
        print(f"[ERROR] {resumes_path} not found. Run Step 3 first.")
        sys.exit(1)

    df_r = pd.read_csv(resumes_path, encoding="utf-8-sig")
    df_j = pd.read_csv(jobs_path, encoding="utf-8-sig")

    # === Resumes ===

    # 1. 学历等级
    df_r["education_level"] = df_r["education"].map(EDUCATION_LEVEL).fillna(3).astype(int)
    print(f"[1] Education levels mapped. Distribution:\n{df_r['education_level'].value_counts().to_string()}")

    # 2. 标准化城市
    df_r["city_normalized"] = df_r["city"].map(lambda x: CITY_MAP.get(str(x).strip(), x))
    df_j["city_normalized"] = df_j["city"].map(lambda x: CITY_MAP.get(str(x).strip(), x))

    # 3. 经验年数（确保为数值）
    df_r["experience_years"] = pd.to_numeric(df_r["experience_years"], errors="coerce").fillna(0).astype(int)
    df_j["min_experience_years"] = pd.to_numeric(df_j["min_experience_years"], errors="coerce").fillna(0).astype(int)
    print(f"[3] Experience years converted. Resume range: {df_r['experience_years'].min()}-{df_r['experience_years'].max()}")

    # 4. 技能列表切分
    def parse_skills(val):
        if not isinstance(val, str) or not val.strip():
            return []
        parts = [s.strip().lower() for s in val.split(";") if s.strip()]
        return parts

    df_r["skills_list"] = df_r["skills"].apply(parse_skills)
    df_j["required_skills_list"] = df_j["required_skills"].apply(parse_skills)

    # 5. 证书列表切分
    df_r["certificates_list"] = df_r["certificates"].apply(parse_skills)
    df_j["preferred_certs_list"] = df_j["preferred_certificates"].apply(parse_skills)
    print(f"[4-5] Skills and certificates parsed into lists.")

    # 6. 薪资确保为数值
    df_r["expected_salary"] = pd.to_numeric(df_r["expected_salary"], errors="coerce").fillna(0).astype(int)
    df_j["salary"] = pd.to_numeric(df_j["salary"], errors="coerce").fillna(0).astype(int)

    # 7. 拼接完整匹配文本（用于后续TF-IDF/Word2Vec）
    def build_full_text(row):
        parts = []
        for col in ["skills", "major", "project_experience", "self_description"]:
            val = str(row.get(col, ""))
            if val and val != "nan":
                parts.append(val)
        return " ".join(parts)

    def build_job_text(row):
        parts = []
        for col in ["job_title", "required_skills", "job_description"]:
            val = str(row.get(col, ""))
            if val and val != "nan":
                parts.append(val)
        return " ".join(parts)

    df_r["full_text"] = df_r.apply(build_full_text, axis=1)
    df_j["full_text"] = df_j.apply(build_job_text, axis=1)
    print(f"[7] Full text columns built.")

    # Save
    out_r = os.path.join(OUTPUT_DIR, "structured_resumes.csv")
    out_j = os.path.join(OUTPUT_DIR, "structured_jobs.csv")
    df_r.to_csv(out_r, index=False, encoding="utf-8-sig")
    df_j.to_csv(out_j, index=False, encoding="utf-8-sig")

    print(f"\n[OK] Structured resumes: {out_r} ({len(df_r)} rows, {len(df_r.columns)} cols)")
    print(f"[OK] Structured jobs:    {out_j} ({len(df_j)} rows, {len(df_j.columns)} cols)")

if __name__ == "__main__":
    structure_data()
