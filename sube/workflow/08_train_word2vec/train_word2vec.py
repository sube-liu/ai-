# -*- coding: utf-8 -*-
"""
第8步：训练Word2Vec
使用gensim训练词向量，生成简历和岗位的文本平均向量。
"""
import pandas as pd
import pickle
import json
import numpy as np
import os
import sys

from gensim.models import Word2Vec

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "workflow", "06_preprocess_text", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_tokens(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    tokens_col = []
    for val in df["tokens"]:
        if isinstance(val, str):
            tokens_col.append(json.loads(val))
        else:
            tokens_col.append([])
    return tokens_col

def average_vector(tokens, model, dim):
    vectors = []
    for t in tokens:
        try:
            v = model.wv[str(t)]
            if isinstance(v, (list, np.ndarray)):
                vectors.append(list(v))
        except (KeyError, IndexError):
            pass
    if len(vectors) == 0:
        return np.zeros(dim, dtype=np.float64)
    return np.array(vectors, dtype=np.float64).mean(axis=0)

def main():
    r_path = os.path.join(INPUT_DIR, "processed_resumes.csv")
    j_path = os.path.join(INPUT_DIR, "processed_jobs.csv")

    if not os.path.exists(r_path):
        print(f"[ERROR] {r_path} not found. Run Step 6 first.")
        sys.exit(1)

    resume_tokens = load_tokens(r_path)
    job_tokens = load_tokens(j_path)
    all_tokens = resume_tokens + job_tokens

    # Filter out empty lists
    all_tokens_filtered = [t for t in all_tokens if len(t) > 0]
    print(f"[DATA] {len(resume_tokens)} resumes, {len(job_tokens)} jobs")
    print(f"[DATA] {len(all_tokens_filtered)} non-empty token lists for training")

    if len(all_tokens_filtered) < 5:
        print("[WARN] Too few training samples. Word2Vec needs more data. Creating a dummy model.")
        # Create a minimal model manually
        all_tokens_filtered = [["python", "sql", "数据分析"]]

    # Train Word2Vec
    print("[TRAIN] Training Word2Vec...")
    model = Word2Vec(
        sentences=all_tokens_filtered,
        vector_size=50,
        window=5,
        min_count=1,
        workers=2,
        epochs=30,
        seed=42
    )
    print(f"[TRAIN] Vocabulary size: {len(model.wv)}")
    print(f"[TRAIN] Vector dimension: {model.wv.vector_size}")

    # Compute average vectors
    dim = model.wv.vector_size
    resume_vecs = np.array([average_vector(t, model, dim) for t in resume_tokens])
    job_vecs = np.array([average_vector(t, model, dim) for t in job_tokens])
    print(f"[VEC] Resume vectors shape: {resume_vecs.shape}")
    print(f"[VEC] Job vectors shape: {job_vecs.shape}")

    # Save
    model_path = os.path.join(OUTPUT_DIR, "word2vec.model")
    rvec_path = os.path.join(OUTPUT_DIR, "resume_w2v_vectors.pkl")
    jvec_path = os.path.join(OUTPUT_DIR, "job_w2v_vectors.pkl")

    model.save(model_path)
    with open(rvec_path, "wb") as f:
        pickle.dump(resume_vecs, f)
    with open(jvec_path, "wb") as f:
        pickle.dump(job_vecs, f)

    print(f"\n[OK] Word2Vec model saved: {model_path}")
    print(f"[OK] Resume vectors:       {rvec_path}")
    print(f"[OK] Job vectors:          {jvec_path}")

    # Show some similar words
    if len(model.wv) > 2:
        try:
            sims = model.wv.most_similar("python", topn=5)
            print(f"\n[SIMILAR to 'python']: {sims}")
        except KeyError:
            print("\n[SIMILAR] 'python' not in vocabulary")

if __name__ == "__main__":
    main()
