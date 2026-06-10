# -*- coding: utf-8 -*-
"""
第6步：文本预处理
jieba分词 + 停用词过滤 + 技能词标准化，输出处理后的CSV。
"""
import pandas as pd
import json
import os
import sys
import re

# jieba might not be installed; wrap import
try:
    import jieba
except ImportError:
    print("[WARN] jieba not installed. Install with: pip install jieba")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_STRUCT = os.path.join(BASE_DIR, "workflow", "04_structure_data", "outputs")
INPUT_RES = os.path.join(BASE_DIR, "workflow", "05_text_resource_analysis", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_resources():
    with open(os.path.join(INPUT_RES, "stopwords.json"), "r", encoding="utf-8") as f:
        stopwords = set(json.load(f))
    with open(os.path.join(INPUT_RES, "skill_alias.json"), "r", encoding="utf-8") as f:
        skill_alias = json.load(f)
    return stopwords, skill_alias

def preprocess_text(text, stopwords, skill_alias):
    """分词 + 去停用词 + 技能标准化"""
    if not isinstance(text, str) or not text.strip():
        return [], ""
    # Clean: remove special chars, keep Chinese + alphanumeric
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9+\-#]", " ", text)
    # Tokenize
    tokens = jieba.lcut(text)
    # Filter: remove stopwords, short tokens, pure digits
    filtered = []
    for t in tokens:
        t = t.strip().lower()
        if len(t) < 2:
            continue
        if t in stopwords:
            continue
        if re.match(r"^\d+$", t):
            continue
        # Skill alias normalization
        t = skill_alias.get(t, t)
        filtered.append(t)
    clean_text = " ".join(filtered)
    return filtered, clean_text

def main():
    resumes_path = os.path.join(INPUT_STRUCT, "structured_resumes.csv")
    jobs_path = os.path.join(INPUT_STRUCT, "structured_jobs.csv")

    if not os.path.exists(resumes_path):
        print(f"[ERROR] {resumes_path} not found. Run Step 4 first.")
        sys.exit(1)

    stopwords, skill_alias = load_resources()
    print(f"[LOAD] {len(stopwords)} stopwords, {len(skill_alias)} skill aliases")

    df_r = pd.read_csv(resumes_path, encoding="utf-8-sig")
    df_j = pd.read_csv(jobs_path, encoding="utf-8-sig")

    # Process resume text
    print("\n[PROCESS] Resumes...")
    tokens_list = []
    clean_texts = []
    for _, row in df_r.iterrows():
        tokens, ct = preprocess_text(row.get("full_text", ""), stopwords, skill_alias)
        tokens_list.append(tokens)
        clean_texts.append(ct)
    df_r["tokens"] = tokens_list
    df_r["clean_text"] = clean_texts

    # Standardize resume skills
    def std_skills(row):
        raw = row.get("skills_list", "[]")
        if isinstance(raw, str):
            import ast
            try:
                raw = ast.literal_eval(raw)
            except:
                raw = []
        result = []
        for s in raw:
            s = s.strip().lower()
            s = skill_alias.get(s, s)
            result.append(s)
        return ";".join(result)

    df_r["standard_skills"] = df_r.apply(std_skills, axis=1)

    # Process job text
    print("[PROCESS] Jobs...")
    j_tokens = []
    j_ct = []
    for _, row in df_j.iterrows():
        tokens, ct = preprocess_text(row.get("full_text", ""), stopwords, skill_alias)
        j_tokens.append(tokens)
        j_ct.append(ct)
    df_j["tokens"] = j_tokens
    df_j["clean_text"] = j_ct

    # Standardize job skills
    def std_job_skills(row):
        raw = row.get("required_skills_list", "[]")
        if isinstance(raw, str):
            import ast
            try:
                raw = ast.literal_eval(raw)
            except:
                raw = []
        result = []
        for s in raw:
            s = s.strip().lower()
            s = skill_alias.get(s, s)
            result.append(s)
        return ";".join(result)

    df_j["required_skills_standard"] = df_j.apply(std_job_skills, axis=1)

    # Save
    out_r = os.path.join(OUTPUT_DIR, "processed_resumes.csv")
    out_j = os.path.join(OUTPUT_DIR, "processed_jobs.csv")
    # Convert list columns to string for CSV storage
    df_r_save = df_r.copy()
    df_r_save["tokens"] = df_r_save["tokens"].apply(lambda x: json.dumps(x, ensure_ascii=False))
    df_j_save = df_j.copy()
    df_j_save["tokens"] = df_j_save["tokens"].apply(lambda x: json.dumps(x, ensure_ascii=False))

    df_r_save.to_csv(out_r, index=False, encoding="utf-8-sig")
    df_j_save.to_csv(out_j, index=False, encoding="utf-8-sig")

    print(f"\n[OK] Processed resumes: {out_r} ({len(df_r)} rows)")
    print(f"[OK] Processed jobs:    {out_j} ({len(df_j)} rows)")
    # Show sample
    print(f"\n[Sample] First resume tokens: {df_r['tokens'].iloc[0]}")
    print(f"[Sample] First job tokens:    {df_j['tokens'].iloc[0]}")

if __name__ == "__main__":
    main()
