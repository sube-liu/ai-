#!/usr/bin/env bash
set -e

cd /home/hadoop/sube

echo "========== 1. Python 环境 =========="
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

echo "========== 2. 启动 HDFS / YARN =========="
start-dfs.sh || true
start-yarn.sh || true

echo "========== 3. HDFS 检查 =========="
hdfs dfs -ls / || true

echo "========== 4. 创建 HDFS 目录 =========="
hdfs dfs -mkdir -p /resume_matching/raw_data
hdfs dfs -mkdir -p /resume_matching/results

echo "========== 5. 上传数据 =========="
hdfs dfs -put -f data/resumes.csv /resume_matching/raw_data/resumes.csv
hdfs dfs -put -f data/jobs.csv /resume_matching/raw_data/jobs.csv

echo "========== 6. 运行 Spark =========="
hdfs dfs -rm -r -f /resume_matching/results/match_results || true

spark-submit src/spark_match_pipeline.py \
  --resumes hdfs:///resume_matching/raw_data/resumes.csv \
  --jobs hdfs:///resume_matching/raw_data/jobs.csv \
  --output hdfs:///resume_matching/results/match_results

echo "========== 7. 拉取 Spark 结果 =========="
mkdir -p workflow/11_build_match_results/outputs
rm -f workflow/11_build_match_results/outputs/match_results.csv

hdfs dfs -getmerge \
  hdfs:///resume_matching/results/match_results \
  workflow/11_build_match_results/outputs/match_results.csv

echo "========== 8. 配置 AI =========="
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="ollama"
export AI_MODEL="qwen2.5:7b"

echo "========== 9. 启动 Streamlit =========="
pkill -f "streamlit run workflow/12_streamlit_web/app.py" || true

nohup python3 -m streamlit run workflow/12_streamlit_web/app.py \
  --server.address 0.0.0.0 \
  --server.port 8501 \
  > streamlit.log 2>&1 &

sleep 3

echo "========== 10. 检查端口 =========="
ss -lntp | grep 8501 || true

echo "启动完成，请访问："
echo "http://$(hostname -I | awk '{print $1}'):8501"
EOF

chmod +x run_all.sh
