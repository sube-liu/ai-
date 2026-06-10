# 人岗智能匹配系统

本项目用于模拟简历与岗位匹配流程，包含脏数据生成、数据探索、清洗、结构化、文本资源分析、文本预处理、TF-IDF、Word2Vec、语义评分、规则评分、最终结果生成和 Streamlit 可视化页面。

## 环境安装

```bash
pip install -r requirements.txt
```

## Ubuntu VM 运行建议

在 Ubuntu 虚拟机中建议先准备 Python、Java 和 Spark：

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv openjdk-11-jdk

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果使用系统 Spark，请确保 `spark-submit` 已加入 `PATH`：

```bash
spark-submit --version
```

如果使用 HDFS，请先启动 Hadoop/HDFS，再执行上传与 Spark 作业。若只是本地演示，可以不启动 HDFS，直接使用本地 CSV 跑完整流程。

## 本地流程

小数据量可以直接运行本地 pandas / scikit-learn / gensim 流程：

```bash
python3 workflow/01_ai_generate_dirty_data/generate_dirty_data.py
python3 workflow/02_data_exploration/data_exploration.py
python3 workflow/03_clean_data/clean_data.py
python3 workflow/04_structure_data/structure_data.py
python3 workflow/05_text_resource_analysis/build_text_resources.py
python3 workflow/06_preprocess_text/preprocess_text.py
python3 workflow/07_train_tfidf/train_tfidf.py
python3 workflow/08_train_word2vec/train_word2vec.py
python3 workflow/09_calculate_semantic_scores/calculate_semantic_scores.py
python3 workflow/10_calculate_rule_scores/calculate_rule_scores.py
python3 workflow/11_build_match_results/build_match_results.py
```

## PySpark / HDFS 改造

根据实训要求，核心计算步骤建议使用 PySpark 改造：

- 第 3-4 步：用 Spark DataFrame 进行缺失值、重复值、学历、城市、经验、薪资和技能字段处理。
- 第 7 步：使用 Spark MLlib 的 `Tokenizer`、`HashingTF`、`IDF` 训练 TF-IDF。
- 第 8 步：使用 Spark MLlib 的 `Word2Vec` 训练词向量。
- 第 9-11 步：使用 Spark DataFrame 计算语义分、规则分并合并最终结果。
- 第 12 步：Streamlit 只读取最终 CSV / Parquet / 数据库结果即可。

本项目已提供 Spark 主流程脚本：

```bash
spark-submit src/spark_match_pipeline.py
```

使用 HDFS 输入输出：

```bash
python3 src/hdfs_utils.py setup
python3 src/hdfs_utils.py upload

spark-submit src/spark_match_pipeline.py \
  --resumes hdfs:///resume_matching/raw_data/resumes.csv \
  --jobs hdfs:///resume_matching/raw_data/jobs.csv \
  --output hdfs:///resume_matching/results/match_results
```

## Streamlit 页面

运行最终结果生成后启动页面：

```bash
python3 -m streamlit run workflow/12_streamlit_web/app.py --server.address 0.0.0.0 --server.port 8501
```

在 Ubuntu 虚拟机中运行后，宿主机浏览器访问 `http://虚拟机IP:8501`。如果访问不到，请检查虚拟机网络模式、防火墙和端口转发。

页面包含：

- 总体界面统计：简历数量、岗位数量、匹配组合数量、最高匹配分。
- 学生推荐岗位：按单个简历查看推荐岗位、分数构成、共同技能、缺少技能和成长建议。
- 岗位推荐候选人：按岗位查看推荐候选人、分数构成、候选人技能和风险标签。
- 数据预览下载：下载匹配结果、结构化简历和结构化岗位数据。

## AI 分析（可选）

如果需要接入本地或云端大模型，可设置以下环境变量，并在 `src/ai_analyzer.py` 中配置模型调用。

```bash
export OPENAI_BASE_URL=http://localhost:11434/v1
export OPENAI_API_KEY=ollama
export AI_MODEL=qwen2.5:7b
```

## 评分公式

```text
total = skill*0.30 + tfidf*0.20 + word2vec*0.15 + education*0.15 + experience*0.10 + city*0.05 + certificate*0.05
```
