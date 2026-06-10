# -*- coding: utf-8 -*-
"""第 11 步：合并语义分和规则分，生成最终匹配结果。"""
from __future__ import annotations

import os

import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_STRUCT = os.path.join(BASE_DIR, "workflow", "04_structure_data", "outputs")
INPUT_SEM = os.path.join(BASE_DIR, "workflow", "09_calculate_semantic_scores", "outputs")
INPUT_RULE = os.path.join(BASE_DIR, "workflow", "10_calculate_rule_scores", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

WEIGHTS = {
    "skill_score": 0.30,
    "tfidf_score": 0.20,
    "word2vec_score": 0.15,
    "education_score": 0.15,
    "experience_score": 0.10,
    "city_score": 0.05,
    "certificate_score": 0.05,
}


def has_text(value: object) -> bool:
    if pd.isna(value):
        return False
    return bool(str(value).strip())


def build_reason(row: pd.Series) -> str:
    parts: list[str] = []

    if has_text(row.get("matched_skills")):
        parts.append("共同技能：" + str(row["matched_skills"]))
    if has_text(row.get("missing_skills")):
        parts.append("缺少技能：" + str(row["missing_skills"]))

    edu = float(row.get("education_score", 0) or 0)
    if edu >= 100:
        parts.append("学历满足要求")
    elif edu >= 50:
        parts.append("学历略低于要求")
    else:
        parts.append("学历不满足要求")

    exp = float(row.get("experience_score", 0) or 0)
    if exp >= 100:
        parts.append("经验满足要求")
    elif exp >= 50:
        parts.append("经验接近要求")
    else:
        parts.append("经验不足")

    tfidf = float(row.get("tfidf_score", 0) or 0)
    if tfidf >= 50:
        parts.append("文本相似度较高")
    elif tfidf >= 30:
        parts.append("文本相似度一般")
    else:
        parts.append("文本相似度较低")

    if edu < 100 and has_text(row.get("missing_skills")):
        parts.append("建议补充" + str(row["missing_skills"]) + "技能")

    return "；".join(parts)


def main() -> None:
    df_r = pd.read_csv(os.path.join(INPUT_STRUCT, "structured_resumes.csv"), encoding="utf-8-sig")
    df_j = pd.read_csv(os.path.join(INPUT_STRUCT, "structured_jobs.csv"), encoding="utf-8-sig")
    df_sem = pd.read_csv(os.path.join(INPUT_SEM, "semantic_scores.csv"), encoding="utf-8-sig")
    df_rule = pd.read_csv(os.path.join(INPUT_RULE, "rule_scores.csv"), encoding="utf-8-sig")

    merged = df_sem.merge(df_rule, on=["resume_id", "job_id"], how="inner")

    total = 0
    for column, weight in WEIGHTS.items():
        total = total + merged[column] * weight
    merged["total_score"] = total.round(1)

    merged["reason"] = merged.apply(build_reason, axis=1)
    merged["company"] = merged["job_id"].map(dict(zip(df_j["job_id"], df_j["company"])))
    merged["resume_education"] = merged["resume_id"].map(dict(zip(df_r["resume_id"], df_r["education"])))

    merged.sort_values("total_score", ascending=False, inplace=True)

    out_path = os.path.join(OUTPUT_DIR, "match_results.csv")
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Match results saved: {out_path} ({len(merged)} rows)")
    print("\n[TOP 10 Matches]:")
    for _, row in merged.head(10).iterrows():
        print(
            "  %s -> %s (%s) | total=%.1f skill=%.1f edu=%.1f"
            % (
                row["name"],
                row["job_title"],
                row.get("company", ""),
                row["total_score"],
                row["skill_score"],
                row["education_score"],
            )
        )


if __name__ == "__main__":
    main()
