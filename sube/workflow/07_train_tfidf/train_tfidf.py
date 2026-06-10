# -*- coding: utf-8 -*-
"""
第7步：训练TF-IDF
对所有简历和岗位文本构建TF-IDF矩阵，保存向量器。
"""
import pandas as pd
import pickle
import os
import sys

from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "workflow", "06_preprocess_text", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    r_path = os.path.join(INPUT_DIR, "processed_resumes.csv")
    j_path = os.path.join(INPUT_DIR, "processed_jobs.csv")

    if not os.path.exists(r_path):
        print(f"[ERROR] {r_path} not found. Run Step 6 first.")
        sys.exit(1)

    df_r = pd.read_csv(r_path, encoding="utf-8-sig")
    df_j = pd.read_csv(j_path, encoding="utf-8-sig")

    # Combine all texts for a shared vocabulary
    all_texts = list(df_r["clean_text"].fillna("")) + list(df_j["clean_text"].fillna(""))
    print(f"[DATA] Total texts: {len(all_texts)} ({len(df_r)} resumes + {len(df_j)} jobs)")

    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        max_features=500,
        ngram_range=(1, 2),
        sublinear_tf=True
    )
    print("[TRAIN] Fitting TF-IDF vectorizer...")
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    print(f"[TRAIN] TF-IDF matrix shape: {tfidf_matrix.shape}")
    print(f"  Vocabulary size: {len(vectorizer.vocabulary_)}")

    # Split back
    n_resumes = len(df_r)
    resume_matrix = tfidf_matrix[:n_resumes]
    job_matrix = tfidf_matrix[n_resumes:]

    # Save
    vec_path = os.path.join(OUTPUT_DIR, "tfidf_vectorizer.pkl")
    rmat_path = os.path.join(OUTPUT_DIR, "resume_tfidf_matrix.pkl")
    jmat_path = os.path.join(OUTPUT_DIR, "job_tfidf_matrix.pkl")

    with open(vec_path, "wb") as f:
        pickle.dump(vectorizer, f)
    with open(rmat_path, "wb") as f:
        pickle.dump(resume_matrix, f)
    with open(jmat_path, "wb") as f:
        pickle.dump(job_matrix, f)

    print(f"\n[OK] TF-IDF vectorizer saved: {vec_path}")
    print(f"[OK] Resume TF-IDF matrix:    {rmat_path}")
    print(f"[OK] Job TF-IDF matrix:       {jmat_path}")

    # Show top features
    feature_names = vectorizer.get_feature_names_out()
    print(f"\n[TOP 20] Feature names: {list(feature_names[:20])}")

if __name__ == "__main__":
    main()
