# -*- coding: utf-8 -*-
"""
第5步：文本资源分析
基于实际数据生成停用词表(skill_alias.json)和技能词标准化表(stopwords.json)。
"""
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "workflow", "04_structure_data", "outputs")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def build_resources():
    # ---- Stopwords ----
    stopwords = [
        # Common Chinese stopwords
        "的", "了", "和", "是", "就", "都", "而", "及", "与", "着",
        "或", "一个", "没有", "我们", "你们", "他们", "她们", "自己",
        "这", "那", "这个", "那个", "这些", "那些", "什么", "哪", "怎么",
        "可以", "可能", "应该", "需要", "已经", "并且", "但是", "因为", "所以",
        "如果", "虽然", "然后", "之后", "之前", "之间", "之中",
        # Resume/job-specific stopwords
        "本人", "熟悉", "负责", "相关", "一定", "较强", "精通", "擅长",
        "参与", "具备", "具有", "能够", "进行", "使用", "了解", "掌握",
        "项目", "经验", "公司", "工作", "内容", "要求", "岗位",
        "认真负责", "学习能力", "团队合作", "沟通能力", "解决问题",
        "数据分析", "大数据", "开发", "设计", "管理", "维护",
        "专业", "方向", "经历", "实习", "获奖", "做过", "一年", "两年",
        # Punctuation-like
        "的", "地", "得", "着", "了", "过",
    ]
    # Remove duplicates
    stopwords = sorted(set(stopwords))

    # ---- Skill Alias (standardization) ----
    skill_alias = {
        "py": "python", "python语言": "python",
        "pyspark": "spark", "sparksql": "spark",
        "结构化查询语言": "sql", "mysql": "sql",
        "hivesql": "hive", "hadoop生态": "hadoop",
        "tensorflow或pytorch": "tensorflow",
        "django/flask": "django",
        "vue/react": "vue",
        "cv或nlp": "nlp",
        "excel": "excel", "excel/表格": "excel",
        "ppt": "ppt",
        "数据可视化": "可视化", "tableau": "可视化",
        "javascript": "javascript", "js": "javascript",
        "html": "html", "css": "css",
        "linux": "linux", "shell": "shell",
        "英语四级": "英语四级", "英语六级": "英语六级",
        "计算机二级": "计算机二级", "软考中级": "软考中级",
        "四级": "英语四级", "二级": "计算机二级",
    }

    # Save
    sw_path = os.path.join(OUTPUT_DIR, "stopwords.json")
    sa_path = os.path.join(OUTPUT_DIR, "skill_alias.json")

    with open(sw_path, "w", encoding="utf-8") as f:
        json.dump(stopwords, f, ensure_ascii=False, indent=2)
    with open(sa_path, "w", encoding="utf-8") as f:
        json.dump(skill_alias, f, ensure_ascii=False, indent=2)

    print(f"[OK] Stopwords saved:    {sw_path} ({len(stopwords)} words)")
    print(f"[OK] Skill aliases saved: {sa_path} ({len(skill_alias)} mappings)")

if __name__ == "__main__":
    build_resources()
