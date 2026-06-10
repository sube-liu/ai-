# -*- coding: utf-8 -*-
"""
第10步：计算规则分
技能分、学历分、经验分、城市分、薪资分、证书分，输出完整的规则评分表。
"""
import pandas as pd
import numpy as np
import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_STRUCT = os.path.join(BASE_DIR, "workflow", "04_structure_data", "outputs")
INPUT_PROC = os.path.join(BASE_DIR, "workflow", "06_preprocess_text", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_skills(val):
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        if val.startswith("["):
            try:
                return json.loads(val)
            except:
                pass
        return [s.strip() for s in val.split(";") if s.strip()]
    return []

def score_skills(resume_skills, job_skills):
    """技能匹配分：交集/并集比例"""
    if not job_skills:
        return 100, [], []  # No requirements = full match
    r_set = set(resume_skills)
    j_set = set(job_skills)
    matched = r_set & j_set
    missing = j_set - r_set
    if len(j_set) == 0:
        return 0, [], list(j_set)
    ratio = len(matched) / len(j_set)
    return round(ratio * 100, 1), list(matched), list(missing)

EDUCATION_LEVEL = {"博士": 5, "硕士": 4, "本科": 3, "大专": 2, "高中": 1, "": 0}

def score_education(resume_edu, job_edu):
    """学历匹配分"""
    r_level = EDUCATION_LEVEL.get(str(resume_edu).strip(), 3)
    j_level = EDUCATION_LEVEL.get(str(job_edu).strip(), 3)
    if r_level >= j_level:
        return 100
    elif r_level == j_level - 1:
        return 50
    else:
        return 0

def score_experience(resume_exp, job_min_exp):
    """经验匹配分"""
    try:
        r_exp = int(resume_exp)
        j_exp = int(job_min_exp)
    except:
        return 0
    if r_exp >= j_exp:
        return 100
    elif r_exp >= j_exp - 1:
        return 50
    return 0

def score_city(resume_city, job_city):
    """城市匹配分"""
    if not resume_city or not job_city:
        return 0
    if str(resume_city).strip() == str(job_city).strip():
        return 100
    return 0

def score_salary(resume_expected, job_salary):
    """薪资匹配分：岗位薪资是否达到期望"""
    try:
        r_sal = int(resume_expected)
        j_sal = int(job_salary)
    except:
        return 50
    if j_sal >= r_sal:
        return 100
    ratio = j_sal / max(r_sal, 1)
    return round(min(100, ratio * 100), 1)

def score_certificates(resume_certs, job_certs):
    """证书匹配分"""
    if not job_certs or not str(job_certs).strip():
        return 100
    r_set = set(parse_skills(resume_certs))
    j_set = set(parse_skills(job_certs))
    if not j_set:
        return 100
    return round(len(r_set & j_set) / len(j_set) * 100, 1)

def main():
    r_path = os.path.join(INPUT_STRUCT, "structured_resumes.csv")
    j_path = os.path.join(INPUT_STRUCT, "structured_jobs.csv")
    p_r_path = os.path.join(INPUT_PROC, "processed_resumes.csv")
    p_j_path = os.path.join(INPUT_PROC, "processed_jobs.csv")

    df_r = pd.read_csv(r_path, encoding="utf-8-sig")
    df_j = pd.read_csv(j_path, encoding="utf-8-sig")
    df_pr = pd.read_csv(p_r_path, encoding="utf-8-sig")
    df_pj = pd.read_csv(p_j_path, encoding="utf-8-sig")

    rows = []
    for i, rr in df_r.iterrows():
        resume_skills = parse_skills(df_pr.iloc[i]["standard_skills"])
        for k, jr in df_j.iterrows():
            job_skills = parse_skills(df_pj.iloc[k]["required_skills_standard"])

            skill_s, matched, missing = score_skills(resume_skills, job_skills)
            edu_s = score_education(rr["education"], jr["required_education"])
            exp_s = score_experience(rr["experience_years"], jr["min_experience_years"])
            city_s = score_city(rr.get("city_normalized", rr.get("city", "")),
                                jr.get("city_normalized", jr.get("city", "")))
            sal_s = score_salary(rr["expected_salary"], jr["salary"])
            cert_s = score_certificates(rr["certificates"], jr["preferred_certificates"])

            rows.append({
                "resume_id": rr["resume_id"],
                "job_id": jr["job_id"],
                "skill_score": skill_s,
                "education_score": edu_s,
                "experience_score": exp_s,
                "city_score": city_s,
                "salary_score": sal_s,
                "certificate_score": cert_s,
                "matched_skills": ";".join(matched),
                "missing_skills": ";".join(missing),
            })

    df_out = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, "rule_scores.csv")
    df_out.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"[OK] Rule scores saved: {out_path} ({len(df_out)} rows)")
    print(f"\n[STATS] Skill score:     avg={df_out['skill_score'].mean():.1f}")
    print(f"        Education score: avg={df_out['education_score'].mean():.1f}")
    print(f"        Experience score:avg={df_out['experience_score'].mean():.1f}")
    print(f"        City score:      avg={df_out['city_score'].mean():.1f}")
    print(f"        Salary score:    avg={df_out['salary_score'].mean():.1f}")
    print(f"        Certificate score: avg={df_out['certificate_score'].mean():.1f}")

if __name__ == "__main__":
    main()
