# -*- coding: utf-8 -*-
"""AI模块 - 大模型API简历-岗位深度匹配分析。支持OpenAI/Ollama等。"""
import json, os, urllib.request, urllib.error

class AIAnalyzer:
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.environ.get("AI_MODEL", "gpt-4o-mini")
        self.available = bool(self.api_key)
    def _call_api(self, messages, temperature=0.3, max_tokens=1200):
        url = self.base_url + "/chat/completions"
        data = json.dumps({"model":self.model,"messages":messages,"temperature":temperature,"max_tokens":max_tokens}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type","application/json")
        req.add_header("Authorization","Bearer "+self.api_key)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError("API HTTP "+str(e.code)+": "+e.read().decode("utf-8",errors="replace")[:300])
        except Exception as e:
            raise RuntimeError("API call failed: "+str(e))
    def analyze_match(self, resume_info, job_info):
        if not self.available:
            return self._fallback_analysis(resume_info, job_info)
        try:
            return self._call_api([
                {"role":"system","content":"你是一位资深HR技术顾问兼职业规划师，擅长从技术栈、行业趋势和个人发展角度分析人岗匹配。请用中文回答，语言专业、具体、有温度。"},
                {"role":"user","content":self._build_prompt(resume_info,job_info)},
            ], max_tokens=1200).strip()
        except Exception as e:
            print("[AI WARN] API failed: "+str(e)+", using fallback.")
            return self._fallback_analysis(resume_info, job_info)
    def analyze_batch(self, resume_info, job_list, top_n=5):
        results = {}
        for job in job_list[:top_n]:
            try:
                results[job.get("job_id","")] = self.analyze_match(resume_info, job)
            except Exception as e:
                results[job.get("job_id","")] = "[分析失败] "+str(e)
        return results
    def _build_prompt(self, resume, job):
        return (
            "你是一位资深HR技术顾问兼职业规划师，请对以下求职者与岗位的匹配度进行深入、具体的分析。\n\n"
            "【求职者信息】\n"
            "- 姓名：%s\n- 学历：%s\n- 专业：%s\n- 技能：%s\n- 经验年限：%s年\n- 期望城市：%s\n- 证书：%s\n- 项目经历：%s\n- 自我描述：%s\n\n"
            "【岗位信息】\n"
            "- 岗位名称：%s\n- 公司类型：%s\n- 学历要求：%s\n- 技能要求：%s\n- 经验要求：%s年以上\n- 工作城市：%s\n- 薪资：%s\n- 证书偏好：%s\n- 岗位描述：%s\n\n"
            "【系统算法评分（仅供参考）】\n"
            "- 技能匹配分：%s\n- TF-IDF文本相似分：%s\n- Word2Vec语义相似分：%s\n- 学历匹配分：%s\n- 经验匹配分：%s\n- 城市匹配分：%s\n- 综合匹配分：%s\n\n"
            "请从以下6个维度给出详细、有深度的分析（每项2-4句话，总计400-600字）：\n\n"
            "1. **匹配等级**：[优秀(>=80)/良好(60-79)/一般(40-59)/较低(<40)]\n"
            "2. **核心优势分析**：结合算法得分和实际能力，分析该候选人的2-3个主要竞争优势，说明这些优势为何对该岗位重要\n"
            "3. **关键差距诊断**：指出最影响匹配度的1-3个短板，解释这些差距在实际工作中可能带来的挑战\n"
            "4. **技能提升路径**：针对缺少的关键技能，给出具体的学习建议（如推荐学习方向、练习项目类型、预计学习周期）\n"
            "5. **职业发展建议**：基于匹配结果和当前技术趋势，建议该候选人未来6-12个月的重点发展方向和可争取的岗位类型\n"
            "6. **综合推荐**：[强烈推荐/推荐/可考虑/不推荐]，用一句话总结核心判断，并说明简历可以从哪些方面优化\n\n"
            "要求：语言专业但亲切、给出可操作的具体建议、避免空洞评价。"
        ) % (
            resume.get("name",""), resume.get("education",""), resume.get("major",""),
            resume.get("skills",""), resume.get("experience_years",""), resume.get("city",""),
            resume.get("certificates",""), resume.get("project_experience",""), resume.get("self_description",""),
            job.get("job_title",""), job.get("company",""), job.get("required_education",""),
            job.get("required_skills",""), job.get("min_experience_years",""), job.get("city",""),
            job.get("salary",""), job.get("preferred_certificates",""), job.get("job_description",""),
            resume.get("skill_score","N/A"), resume.get("tfidf_score","N/A"), resume.get("word2vec_score","N/A"),
            resume.get("education_score","N/A"), resume.get("experience_score","N/A"),
            resume.get("city_score","N/A"), resume.get("total_score","N/A")
        )

    def _fallback_analysis(self, resume, job):
        total = resume.get("total_score", 0)
        skill_s = resume.get("skill_score", 0)
        edu_s = resume.get("education_score", 0)
        exp_s = resume.get("experience_score", 0)
        tfidf_s = resume.get("tfidf_score", 0)
        w2v_s = resume.get("word2vec_score", 0)
        matched = resume.get("matched_skills", "")
        missing = resume.get("missing_skills", "")
        level = "优秀" if total>=80 else ("良好" if total>=60 else ("一般" if total>=40 else "较低"))
        recommend = "强烈推荐" if total>=85 else ("推荐" if total>=70 else ("可考虑" if total>=50 else "不推荐"))
        lines = [
            "## AI深度分析报告\n",
            "### 1. 匹配等级：**" + level + "**（综合分：" + str(total) + "）\n",
            "### 2. 核心优势分析",
            "- 技能匹配度" + ("较高" if skill_s>=70 else "一般") + "（" + str(skill_s) + "分）：" + ("具备岗位所需的大部分核心技能" if skill_s>=70 else "与岗位要求存在一定差距"),
            "- TF-IDF文本相似度" + str(tfidf_s) + "分，Word2Vec语义相似度" + str(w2v_s) + "分",
            "- 学历匹配：" + ("满足要求（" + str(edu_s) + "分）" if edu_s>=100 else "略低于要求（" + str(edu_s) + "分）") + "，经验匹配：" + str(exp_s) + "分\n",
        ]
        if matched: lines.append("- 共同技能：**" + str(matched) + "**")
        lines.append("\n### 3. 关键差距诊断")
        if missing: lines.append("- 缺少技能：**" + str(missing) + "**，这些是该岗位的核心要求，差距较大")
        if edu_s < 100: lines.append("- 学历要求未完全满足，可能在简历筛选中处于劣势")
        if exp_s < 100: lines.append("- 经验年限不足，建议通过项目实践弥补")
        lines.append("\n### 4. 技能提升路径")
        if missing:
            for ms in str(missing).split(";"):
                if ms.strip():
                    lines.append("- **" + ms.strip() + "**：建议通过在线课程（如Coursera/B站）+ 实战项目练习，预计2-4周可掌握基础")
        lines.append("- 多参与开源项目或Kaggle竞赛，积累可展示的项目经验")
        lines.append("\n### 5. 职业发展建议")
        lines.append("- 建议未来6个月重点提升" + (str(missing)[:60] if missing else "核心技能") + "，增加项目深度")
        lines.append("- 可关注与当前技能栈匹配度更高的岗位类型，逐步向目标岗位过渡")
        lines.append("\n### 6. 综合推荐：**" + recommend + "**")
        if total >= 70:
            lines.append("该候选人与岗位的匹配度较高，建议投递并准备面试。可在简历中突出" + str(matched)[:40] + "等相关经验。")
        elif total >= 50:
            lines.append("该候选人有潜力但存在差距，建议补充关键技能后再投递，或先申请要求稍低的岗位积累经验。")
        else:
            lines.append("当前匹配度较低，建议先系统提升核心技能，再考虑投递该岗位。")
        return "\n".join(lines)


def create_analyzer():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "")
    model = os.environ.get("AI_MODEL", "gpt-4o-mini")
    if api_key:
        print("[AI] Model: "+model)
    else:
        print("[AI] No API key. Set OPENAI_API_KEY to enable. Local: OPENAI_BASE_URL=http://localhost:11434/v1 AI_MODEL=qwen2.5:7b")
    return AIAnalyzer(api_key=api_key, base_url=base_url if base_url else None, model=model)