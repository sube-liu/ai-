# -*- coding: utf-8 -*-
"""
第9步：计算语义分
基于TF-IDF和Word2Vec矩阵，计算每个简历-岗位对的余弦相似度，加权合成语义分。
"""
import pandas as pd
import pickle
import numpy as np
import os
import sys

from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_PROC = os.path.join(BASE_DIR, "workflow", "06_preprocess_text", "outputs")
INPUT_TFIDF = os.path.join(BASE_DIR, "workflow", "07_train_tfidf", "outputs")
INPUT_W2V = os.path.join(BASE_DIR, "workflow", "08_train_word2vec", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def score_to_100(val):
    """Convert cosine similarity to 0-100 score."""
    return round(max(0, min(100, val * 100)), 1)

def main():
    # Load data
    df_r = pd.read_csv(os.path.join(INPUT_PROC, "processed_resumes.csv"), encoding="utf-8-sig")
    df_j = pd.read_csv(os.path.join(INPUT_PROC, "processed_jobs.csv"), encoding="utf-8-sig")

    with open(os.path.join(INPUT_TFIDF, "resume_tfidf_matrix.pkl"), "rb") as f:
        r_tfidf = pickle.load(f)
    with open(os.path.join(INPUT_TFIDF, "job_tfidf_matrix.pkl"), "rb") as f:
        j_tfidf = pickle.load(f)
    with open(os.path.join(INPUT_W2V, "resume_w2v_vectors.pkl"), "rb") as f:
        r_w2v = pickle.load(f)
    with open(os.path.join(INPUT_W2V, "job_w2v_vectors.pkl"), "rb") as f:
        j_w2v = pickle.load(f)

    n_r = len(df_r)
    n_j = len(df_j)
    print(f"[DATA] {n_r} resumes x {n_j} jobs = {n_r * n_j} pairs")

    # Compute cosine similarities
    print("[CALC] TF-IDF cosine similarity...")
    tfidf_sim = cosine_similarity(r_tfidf, j_tfidf)  # (n_r, n_j)

    print("[CALC] Word2Vec cosine similarity...")
    w2v_sim = cosine_similarity(r_w2v, j_w2v)  # (n_r, n_j)

    # Build result DataFrame
    rows = []
    for i in range(n_r):
        for k in range(n_j):
            tfidf_score = score_to_100(tfidf_sim[i, k])
            w2v_score = score_to_100(w2v_sim[i, k])
            # Weighted: TF-IDF 60%, Word2Vec 40%
            semantic_score = round(tfidf_score * 0.6 + w2v_score * 0.4, 1)

            rows.append({
                "resume_id": df_r.iloc[i]["resume_id"],
                "name": df_r.iloc[i]["name"],
                "job_id": df_j.iloc[k]["job_id"],
                "job_title": df_j.iloc[k]["job_title"],
                "tfidf_score": tfidf_score,
                "word2vec_score": w2v_score,
                "semantic_score": semantic_score,
            })

    df_scores = pd.DataFrame(rows)
    out_path = os.path.join(OUTPUT_DIR, "semantic_scores.csv")
    df_scores.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"\n[OK] Semantic scores saved: {out_path} ({len(df_scores)} rows)")
    print(f"\n[TOP 5 by semantic_score]:")
    top5 = df_scores.nlargest(5, "semantic_score")
    print(top5.to_string(index=False))

if __name__ == "__main__":
    main()
