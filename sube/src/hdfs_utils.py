# -*- coding: utf-8 -*-
"""HDFS操作工具模块。封装常用的HDFS命令操作。"""
import subprocess, os, sys

HDFS_BASE = "/resume_matching"

def run_hdfs(cmd, check=True):
    """执行HDFS命令并返回输出。"""
    full_cmd = f"hdfs dfs {cmd}"
    print(f"[HDFS] {full_cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"[HDFS ERROR] {result.stderr}")
    else:
        print(result.stdout.strip())
    return result

def setup_directories():
    """创建HDFS项目目录结构。"""
    print("=" * 50)
    print("Setting up HDFS directories...")
    print("=" * 50)
    dirs = [
        f"{HDFS_BASE}/raw_data",
        f"{HDFS_BASE}/cleaned_data",
        f"{HDFS_BASE}/results",
    ]
    for d in dirs:
        run_hdfs(f"-mkdir -p {d}")
    run_hdfs(f"-ls {HDFS_BASE}")
    print("HDFS directories ready.")

def upload_file(local_path, hdfs_dir):
    """上传本地文件到HDFS。"""
    hdfs_path = f"{hdfs_dir}/{os.path.basename(local_path)}"
    return run_hdfs(f"-put -f {local_path} {hdfs_path}")

def download_file(hdfs_path, local_path):
    """从HDFS下载文件到本地。"""
    return run_hdfs(f"-get {hdfs_path} {local_path}")

def list_dir(hdfs_dir):
    """列出HDFS目录内容。"""
    return run_hdfs(f"-ls {hdfs_dir}")

def delete_path(hdfs_path):
    """删除HDFS路径。"""
    return run_hdfs(f"-rm -r -f {hdfs_path}")

def upload_all_data():
    """上传resumes.csv和jobs.csv到HDFS。"""
    base_local = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    resumes = os.path.join(base_local, "resumes.csv")
    jobs = os.path.join(base_local, "jobs.csv")
    if os.path.exists(resumes):
        upload_file(resumes, f"{HDFS_BASE}/raw_data")
    if os.path.exists(jobs):
        upload_file(jobs, f"{HDFS_BASE}/raw_data")
    run_hdfs(f"-ls {HDFS_BASE}/raw_data")

def check_hdfs_available():
    """检查HDFS是否可用。"""
    try:
        result = subprocess.run("hdfs dfs -ls /", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("[HDFS] HDFS is available.")
            return True
        else:
            print(f"[HDFS] HDFS not available: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"[HDFS] HDFS check failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hdfs_utils.py <command> [args]")
        print("Commands: setup, upload, list, check")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "setup":
        setup_directories()
    elif cmd == "upload":
        upload_all_data()
    elif cmd == "list":
        list_dir(f"{HDFS_BASE}/raw_data")
    elif cmd == "check":
        check_hdfs_available()
    else:
        print(f"Unknown command: {cmd}")
