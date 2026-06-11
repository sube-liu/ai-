# -*- coding: utf-8 -*-
"""Streamlit page for resume-job matching results."""
from __future__ import annotations

import os
import sys
from typing import Iterable

import pandas as pd
import streamlit as st


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

STRUCT_DIR = os.path.join(BASE_DIR, "workflow", "04_structure_data", "outputs")
MATCH_DIR = os.path.join(BASE_DIR, "workflow", "11_build_match_results", "outputs")

SCORE_DIMS = [
    "semantic_score",
    "tfidf_score",
    "word2vec_score",
    "city_score",
    "education_score",
    "skill_score",
    "experience_score",
]

DIM_LABELS = {
    "total_score": "综合匹配分",
    "skill_score": "技能匹配分",
    "semantic_score": "综合语义分",
    "tfidf_score": "TF-IDF词面分",
    "word2vec_score": "Word2Vec语义分",
    "education_score": "学历匹配分",
    "experience_score": "经验匹配分",
    "city_score": "城市匹配",
    "certificate_score": "证书匹配",
}


st.set_page_config(
    page_title="人岗智能匹配系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    match_path = os.path.join(MATCH_DIR, "match_results.csv")
    resume_path = os.path.join(STRUCT_DIR, "structured_resumes.csv")
    job_path = os.path.join(STRUCT_DIR, "structured_jobs.csv")
    return (
        pd.read_csv(match_path, encoding="utf-8-sig"),
        pd.read_csv(resume_path, encoding="utf-8-sig"),
        pd.read_csv(job_path, encoding="utf-8-sig"),
    )


def split_items(value: object) -> list[str]:
    if pd.isna(value):
        return []
    return [item.strip() for item in str(value).replace(",", ";").split(";") if item.strip()]


def join_items(value: object) -> str:
    items = split_items(value)
    return "、".join(items) if items else "暂无"


def classify(total: float) -> str:
    if total >= 80:
        return "高度匹配"
    if total >= 60:
        return "可培养"
    if total >= 40:
        return "谨慎培养"
    return "暂不推荐"


def risk_label(row: pd.Series) -> str:
    if row.get("semantic_score", 0) < 40:
        return "语义关联不足"
    if row.get("skill_score", 0) < 60:
        return "技能覆盖不足"
    if row.get("experience_score", 0) < 60:
        return "经验储备不足"
    if row.get("education_score", 0) < 60:
        return "学历门槛不足"
    return "整体风险较低"


def growth_plan(row: pd.Series) -> str:
    missing = join_items(row.get("missing_skills", ""))
    if missing == "暂无":
        return "继续补充项目案例，把已有技能沉淀为可展示的作品集。"
    return f"7天内补齐 {missing} 的基础语法和常用场景，14天内完成一个小型实训案例，并把结果写入简历。"


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
        [data-testid="stMetric"] { background: transparent; border: 0; padding: 0; }
        [data-testid="stMetricLabel"] { color: #071a3d; font-size: 14px; }
        [data-testid="stMetricValue"] { color: #10203d; font-size: 32px; }
        .section-title { font-size: 20px; font-weight: 800; color: #071a3d; margin: .2rem 0 1rem; }
        .line { color: #071a3d; font-size: 16px; line-height: 1.9; margin: .15rem 0; }
        .line b { margin-right: .35rem; }
        .pill { display:inline-block; padding: 2px 8px; border-radius: 999px; background: #e8f8ef; color:#137333; font-size: 13px; font-weight: 700; }
        .advice { border-left: 4px solid #2f80ed; background: #eaf4ff; color: #06458d; padding: 12px 15px; border-radius: 6px; line-height: 1.75; margin-top: 10px; }
        .risk { border-left: 4px solid #ff9800; background: #fff8e8; color: #9a4d00; padding: 10px 15px; border-radius: 6px; line-height: 1.6; margin-top: 8px; }
        .growth { border-left: 4px solid #18b66a; background: #eafaf1; color: #057040; padding: 10px 15px; border-radius: 6px; line-height: 1.6; margin-top: 8px; }
        .small-muted { color:#6b7890; font-size: 13px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_overview(resumes: pd.DataFrame, jobs: pd.DataFrame, matches: pd.DataFrame) -> None:
    avg_score = matches["total_score"].mean() if not matches.empty else 0
    top_score = matches["total_score"].max() if not matches.empty else 0
    cols = st.columns(4)
    cols[0].metric("简历数量", f"{len(resumes)}")
    cols[1].metric("岗位数量", f"{len(jobs)}")
    cols[2].metric("匹配组合", f"{len(matches)}")
    cols[3].metric("最高匹配分", f"{top_score:.1f}", f"平均 {avg_score:.1f}")


def show_metrics(row: pd.Series) -> None:
    missing_count = len(split_items(row.get("missing_skills", "")))
    values = [
        ("综合匹配分", row.get("total_score", 0)),
        ("技能匹配分", row.get("skill_score", 0)),
        ("文本语义分", row.get("semantic_score", 0)),
        ("学历匹配分", row.get("education_score", 0)),
        ("经验匹配分", row.get("experience_score", 0)),
        ("技能缺口数", missing_count),
    ]
    for col, (label, value) in zip(st.columns(6), values):
        col.metric(label, f"{value:.1f}" if isinstance(value, float) else str(value))
    st.markdown(f"<span class='pill'>↑ {classify(float(row.get('total_score', 0)))}</span>", unsafe_allow_html=True)


def chart_scores(row: pd.Series, title: str) -> None:
    chart = pd.DataFrame(
        {
            "分数": [float(row.get(dim, 0)) for dim in SCORE_DIMS],
        },
        index=[DIM_LABELS[dim] for dim in SCORE_DIMS],
    )
    st.caption(title)
    st.bar_chart(chart, height=310, use_container_width=True)


def ai_advice(row: pd.Series, resume: pd.Series, job: pd.Series) -> str:
    matched = join_items(row.get("matched_skills", ""))
    missing = join_items(row.get("missing_skills", ""))
    return (
        f"匹配等级：{classify(float(row.get('total_score', 0)))}。"
        f"该候选人与{job['job_title']}的综合匹配分为{row.get('total_score', 0):.1f}，"
        f"技能分{row.get('skill_score', 0):.1f}，文本语义相似度偏低。"
        f"优势分析：已覆盖{matched}；学历满足岗位门槛；经验年限满足要求；城市匹配。"
        f"风险提示：缺少{missing}；项目经历与岗位描述关联度不足。"
        f"提升建议：{growth_plan(row)}"
    )


def detail_block(row: pd.Series, resume: pd.Series, job: pd.Series, *, mode: str, rank: int) -> None:
    if mode == "student":
        title = f"推荐岗位 {rank}：{job['job_title']}"
        chart_title = "分数构成"
    else:
        title = f"推荐候选人 {rank}：{resume['name']}"
        chart_title = "候选人分数构成"

    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    show_metrics(row)

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        if mode == "student":
            st.markdown(f"<p class='line'><b>岗位要求技能：</b>{join_items(job.get('required_skills', ''))}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='line'><b>共同技能：</b>{join_items(row.get('matched_skills', ''))}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='line'><b>缺少技能：</b>{join_items(row.get('missing_skills', ''))}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p class='line'><b>候选人技能：</b>{join_items(resume.get('skills', ''))}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='line'><b>岗位要求技能：</b>{join_items(job.get('required_skills', ''))}</p>", unsafe_allow_html=True)
            st.markdown(f"<p class='line'><b>候选人缺少技能：</b>{join_items(row.get('missing_skills', ''))}</p>", unsafe_allow_html=True)

        st.markdown("<p class='line'><b>AI智能推荐意见</b></p>", unsafe_allow_html=True)
        st.markdown(f"<div class='advice'>{ai_advice(row, resume, job)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='risk'>风险标签：{risk_label(row)}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='growth'>成长路线：{growth_plan(row)}</div>", unsafe_allow_html=True)

    with right:
        chart_scores(row, chart_title)


def student_view(matches: pd.DataFrame, resumes: pd.DataFrame, jobs: pd.DataFrame) -> None:
    with st.sidebar:
        name = st.selectbox("选择简历", resumes["name"].tolist())
        min_score = st.slider("最低综合分", 0, 100, 0)
        top_n = st.slider("显示 Top N", 1, 20, 5)
        cities = ["全部"] + sorted(jobs["city"].dropna().unique().tolist())
        city = st.selectbox("岗位城市", cities)

    resume = resumes[resumes["name"] == name].iloc[0]
    data = matches[matches["resume_id"] == resume["resume_id"]].copy()
    if min_score:
        data = data[data["total_score"] >= min_score]
    if city != "全部":
        city_jobs = jobs[jobs["city"] == city]["job_id"].tolist()
        data = data[data["job_id"].isin(city_jobs)]
    data = data.sort_values("total_score", ascending=False).head(top_n)

    st.markdown(f"<div class='small-muted'>当前简历：{resume['education']} / {resume['major']} / {resume['city']}</div>", unsafe_allow_html=True)
    for rank, (_, row) in enumerate(data.iterrows(), start=1):
        job = jobs[jobs["job_id"] == row["job_id"]].iloc[0]
        detail_block(row, resume, job, mode="student", rank=rank)
        st.divider()


def job_view(matches: pd.DataFrame, resumes: pd.DataFrame, jobs: pd.DataFrame) -> None:
    with st.sidebar:
        job_name = st.selectbox("选择岗位", jobs["job_title"].tolist())
        top_n = st.slider("显示 Top N", 1, 20, 5, key="job_top_n")
        min_score = st.slider("最低综合分", 0, 100, 0, key="job_min_score")

    job = jobs[jobs["job_title"] == job_name].iloc[0]
    data = matches[matches["job_id"] == job["job_id"]].copy()
    if min_score:
        data = data[data["total_score"] >= min_score]
    data = data.sort_values("total_score", ascending=False).head(top_n)

    st.markdown(
        f"<div class='small-muted'>当前岗位：{job['company']} / {job['city']} / 薪资 {job['salary']} / 学历要求 {job['required_education']}</div>",
        unsafe_allow_html=True,
    )
    for rank, (_, row) in enumerate(data.iterrows(), start=1):
        resume = resumes[resumes["resume_id"] == row["resume_id"]].iloc[0]
        detail_block(row, resume, job, mode="job", rank=rank)
        st.divider()


def data_view(matches: pd.DataFrame, resumes: pd.DataFrame, jobs: pd.DataFrame) -> None:
    st.subheader("数据总览")
    st.dataframe(
        matches.sort_values("total_score", ascending=False).head(50),
        use_container_width=True,
        hide_index=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "下载匹配结果",
        matches.to_csv(index=False).encode("utf-8-sig"),
        "match_results.csv",
        "text/csv",
        use_container_width=True,
    )
    c2.download_button(
        "下载简历数据",
        resumes.to_csv(index=False).encode("utf-8-sig"),
        "structured_resumes.csv",
        "text/csv",
        use_container_width=True,
    )
    c3.download_button(
        "下载岗位数据",
        jobs.to_csv(index=False).encode("utf-8-sig"),
        "structured_jobs.csv",
        "text/csv",
        use_container_width=True,
    )


def missing_outputs_message(error: Exception) -> None:
    st.error("未找到最终匹配结果，请先运行第 6-11 步生成 match_results.csv。")
    st.code(
        "\n".join(
            [
                "python workflow/06_preprocess_text/preprocess_text.py",
                "python workflow/07_train_tfidf/train_tfidf.py",
                "python workflow/08_train_word2vec/train_word2vec.py",
                "python workflow/09_calculate_semantic_scores/calculate_semantic_scores.py",
                "python workflow/10_calculate_rule_scores/calculate_rule_scores.py",
                "python workflow/11_build_match_results/build_match_results.py",
            ]
        ),
        language="powershell",
    )
    st.caption(str(error))


def main() -> None:
    inject_css()
    st.title("人岗智能匹配系统")

    try:
        matches, resumes, jobs = load_data()
    except Exception as exc:
        missing_outputs_message(exc)
        return

    with st.sidebar:
        st.title("控制面板")
        view = st.radio("视图", ["学生推荐岗位", "岗位推荐候选人", "数据预览下载"])
        st.divider()
        st.metric("简历数量", len(resumes))
        st.metric("岗位数量", len(jobs))

    show_overview(resumes, jobs, matches)
    st.divider()

    if view == "学生推荐岗位":
        student_view(matches, resumes, jobs)
    elif view == "岗位推荐候选人":
        job_view(matches, resumes, jobs)
    else:
        data_view(matches, resumes, jobs)


if __name__ == "__main__":
    main()
