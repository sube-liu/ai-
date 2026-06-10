# -*- coding: utf-8 -*-
"""
第1步：生成脏数据
用程序模拟 AI 生成简历和岗位数据，并故意混入一些数据质量问题（空值、格式不统一等）。
"""
import pandas as pd
import random
import os

random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# 简历数据
# ============================================================
resumes = [
    # resume_id, name, education, major, skills, experience_years, city, expected_salary, certificates, project_experience, self_description
    ["R001", "张同学", "本科", "数据科学与大数据技术", "Python;SQL;Spark;数据分析", 0, "南昌", 5000, "英语四级;计算机二级", "做过数据分析课程项目，使用Python进行数据清洗和可视化", "熟悉Python和数据清洗"],
    ["R002", "李同学", "硕士", "计算机科学与技术", "Java;Python;MySQL;Spring Boot;Hadoop", 1, "北京", 12000, "英语六级;软考中级", "参与过企业级Java项目开发，熟悉微服务架构", "精通Java开发，有实际项目经验"],
    ["R003", "王同学", "本科", "软件工程", "Python;SQL;Excel;数据可视化", 0, "上海", 6000, "英语四级", "毕业设计做了数据可视化大屏", "对数据分析感兴趣"],
    ["R004", "赵同学", "大专", "计算机应用技术", "Java;HTML;CSS;JavaScript", 2, "深圳", 8000, "", "在一家外包公司做过前端开发", "两年开发经验"],
    ["R005", "孙同学", "硕士", "统计学", "R;Python;SQL;SAS;机器学习", 0, "南昌", 7000, "英语六级;计算机二级", "参与导师的统计建模项目", "熟悉统计分析和机器学习"],
    ["R006", "周同学", "本科", "数据科学与大数据技术", "Python;Spark;Hadoop;SQL;Hive", 0, "杭州", 5500, "英语四级;计算机二级", "课程做过Spark数据处理项目", "学习能力强"],
    ["R007", "吴同学", "硕士", "人工智能", "Python;TensorFlow;PyTorch;SQL", 1, "北京", 15000, "英语六级", "发表过一篇NLP方向的论文", "专注深度学习方向"],
    ["R008", "郑同学", "本科", "信息管理与信息系统", "SQL;Python;Excel;Tableau", 1, "深圳", 7000, "英语四级", "实习参与过BI报表搭建", "熟悉数据分析和BI工具"],
    ["R009", "钱同学", "本科", "数学与应用数学", "Python;MATLAB;SQL", 0, "武汉", 5000, "英语四级;计算机二级", "数学建模竞赛获奖", "数学基础扎实"],
    ["R010", "刘同学", "", "计算机科学与技术", "C++;Python;Linux", 0, "北京", 6000, "", "做过嵌入式系统项目", "对底层技术感兴趣"],  # 学历缺失
    ["R011", "陈同学", "本科", "电子商务", "Python;SQL;Excel;PPT", 1, "广州", 5500, "英语四级", "运营过一个电商店铺", "有数据分析基础"],
    ["R012", "黄同学", "硕士", "软件工程", "Java;Python;Go;Docker;K8s", 2, "上海", 18000, "英语六级", "在互联网公司做过后端开发实习", "有微服务项目经验"],
    ["R013", "林同学", "本科", "网络工程", "Python;Shell;Linux;网络安全", 0, "南昌", 5000, "英语四级", "参加过网络安全CTF比赛", "熟悉Linux系统管理"],
    ["R014", "杨同学", "大专", "软件技术", "Java;Spring;MySQL", 1, "成都", 6500, "", "做过一个小型CRM系统", "能独立完成Java Web项目"],
    ["R015", "许同学", "硕士", "计算机科学与技术", "Python;Spark;Scala;Kafka", 0, "杭州", 7000, "英语六级", "研究大数据流处理方向", "对大数据生态有系统学习"],
    ["R016", "何同学", "本科", "物联网工程", "C;Python;嵌入式;传感器", 0, "南京", 5000, "英语四级", "做过智能家居原型项目", "对物联网有热情"],  # 技能与大数据岗相关性低
    ["R017", "吕同学", "硕士", "人工智能", "Python;NLP;Transformer;BERT", 0, "北京", 13000, "英语六级;软考中级", "做过情感分析和文本分类项目", "专注NLP方向"],
    ["R018", "施同学", "本科", "计算机科学与技术", " ", 2, "深圳", 9000, "英语四级", "全栈开发经验，Vue+SpringBoot", "有全栈开发能力"],  # 技能字段为空
    ["R019", "张同学二期", "本科", "数据科学与大数据技术", "excel;;hivesql", 0, "", 5000, "四级;二级", "课程设计做数据分析", "认真负责"],  # 多个数据质量问题：技能格式差、城市缺失、证书格式不统一
    ["R020", "小明", "硕士", "统计学", "R;Python;SQL;SPSS;机器学习;深度学习", 1, "厦门", 10000, "英语六级", "统计建模获奖，有数据分析实习经历", "擅长统计建模"],
]

# ============================================================
# 岗位数据
# ============================================================
jobs = [
    # job_id, job_title, company, required_education, required_skills, min_experience_years, city, salary, preferred_certificates, job_description
    ["J001", "数据分析实习生", "某科技公司", "本科", "Python;SQL;数据分析;Excel", 0, "南昌", 6000, "英语四级", "负责数据清洗、统计分析和报表制作"],
    ["J002", "大数据开发实习生", "某互联网公司", "本科", "Java;Hadoop;Spark;SQL", 0, "南昌", 7000, "计算机二级", "参与大数据平台开发和维护"],
    ["J003", "Python开发工程师", "某软件公司", "本科", "Python;Django/Flask;MySQL;Linux", 1, "北京", 12000, "", "负责后端服务开发和数据库设计"],
    ["J004", "机器学习实习生", "某AI公司", "硕士", "Python;机器学习;深度学习;TensorFlow或PyTorch", 0, "北京", 8000, "英语六级", "参与机器学习模型训练和部署"],
    ["J005", "Java后端工程师", "某金融科技公司", "本科", "Java;Spring Boot;MySQL;Redis", 2, "上海", 15000, "英语四级", "负责金融系统后端开发"],
    ["J006", "数据工程师", "某电商平台", "本科", "SQL;Python;Spark;ETL;数据仓库", 1, "杭州", 13000, "", "建设和维护数据仓库和ETL流程"],
    ["J007", "自然语言处理实习生", "某研究院", "硕士", "Python;NLP;PyTorch;TensorFlow", 0, "北京", 6000, "英语六级", "参与NLP算法研发和论文复现"],
    ["J008", "前端开发工程师", "某互联网公司", "本科", "JavaScript;Vue/React;HTML;CSS", 1, "深圳", 11000, "", "负责Web前端页面开发"],
    ["J009", "数据分析师", "某咨询公司", "本科", "SQL;Excel;Python;Tableau;数据分析", 1, "上海", 10000, "英语四级", "为客户提供数据驱动的业务分析"],
    ["J010", "大数据运维工程师", "某运营商", "本科", "Linux;Hadoop;Shell;Python", 1, "广州", 9000, "", "负责大数据平台的运维和监控"],
    ["J011", "AI算法实习生", "某科技公司", "硕士", "Python;机器学习;深度学习;CV或NLP", 0, "深圳", 7000, "英语六级", "参与计算机视觉或自然语言处理项目"],
    ["J012", "数据分析岗", "", "本科", "Excel;SQL;python", 1, "南昌", 5000, "", ""],  # 公司名空、岗位描述空、技能格式不统一
]

# ============================================================
# 构建 DataFrame
# ============================================================
resume_cols = [
    "resume_id", "name", "education", "major", "skills",
    "experience_years", "city", "expected_salary", "certificates",
    "project_experience", "self_description"
]

job_cols = [
    "job_id", "job_title", "company", "required_education",
    "required_skills", "min_experience_years", "city", "salary",
    "preferred_certificates", "job_description"
]

df_resumes = pd.DataFrame(resumes, columns=resume_cols)
df_jobs = pd.DataFrame(jobs, columns=job_cols)

# ============================================================
# 保存
# ============================================================
resume_path = os.path.join(OUTPUT_DIR, "raw_resumes_dirty.csv")
job_path = os.path.join(OUTPUT_DIR, "raw_jobs_dirty.csv")

df_resumes.to_csv(resume_path, index=False, encoding="utf-8-sig")
df_jobs.to_csv(job_path, index=False, encoding="utf-8-sig")

print(f"[OK] Generated: {resume_path} ({len(df_resumes)} rows)")
print(f"[OK] Generated: {job_path} ({len(df_jobs)} rows)")
print(f"\n=== Resume Data Preview ===")
print(df_resumes.to_string())
print(f"\n=== Job Data Preview ===")
print(df_jobs.to_string())
print(f"\n=== Data Quality Issues ===")
print("- R010: education field is empty")
print("- R018: skills field is empty")
print("- R019: skills separator inconsistent (;;) / city missing / certificate format inconsistent")
print("- J012: company empty / job_description empty / skill format inconsistent (python vs Python)")
