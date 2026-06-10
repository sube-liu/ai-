# Data Exploration Report

```text
============================================================
DATA EXPLORATION REPORT
============================================================

--- 1. Data Scale ---
Resumes: 20 rows, 11 columns
Jobs:    12 rows, 10 columns

--- 2. Resume Fields ---
['resume_id', 'name', 'education', 'major', 'skills', 'experience_years', 'city', 'expected_salary', 'certificates', 'project_experience', 'self_description']

--- 2. Job Fields ---
['job_id', 'job_title', 'company', 'required_education', 'required_skills', 'min_experience_years', 'city', 'salary', 'preferred_certificates', 'job_description']

--- 3. Resumes First 5 Rows ---
  resume_id name education       major                                skills  experience_years city  expected_salary certificates             project_experience  self_description
0      R001  张同学        本科  数据科学与大数据技术                 Python;SQL;Spark;数据分析                 0   南昌             5000   英语四级;计算机二级  做过数据分析课程项目，使用Python进行数据清洗和可视化     熟悉Python和数据清洗
1      R002  李同学        硕士    计算机科学与技术  Java;Python;MySQL;Spring Boot;Hadoop                 1   北京            12000    英语六级;软考中级         参与过企业级Java项目开发，熟悉微服务架构  精通Java开发，有实际项目经验
2      R003  王同学        本科        软件工程                Python;SQL;Excel;数据可视化                 0   上海             6000         英语四级                  毕业设计做了数据可视化大屏          对数据分析感兴趣
3      R004  赵同学        大专     计算机应用技术              Java;HTML;CSS;JavaScript                 2   深圳             8000          NaN                  在一家外包公司做过前端开发            两年开发经验
4      R005  孙同学        硕士         统计学                 R;Python;SQL;SAS;机器学习                 0   南昌             7000   英语六级;计算机二级                    参与导师的统计建模项目       熟悉统计分析和机器学习

--- 3. Jobs First 5 Rows ---
  job_id    job_title  company required_education                      required_skills  min_experience_years city  salary preferred_certificates   job_description
0   J001      数据分析实习生    某科技公司                 本科                Python;SQL;数据分析;Excel                     0   南昌    6000                   英语四级  负责数据清洗、统计分析和报表制作
1   J002     大数据开发实习生   某互联网公司                 本科                Java;Hadoop;Spark;SQL                     0   南昌    7000                  计算机二级      参与大数据平台开发和维护
2   J003  Python开发工程师    某软件公司                 本科      Python;Django/Flask;MySQL;Linux                     1   北京   12000                    NaN    负责后端服务开发和数据库设计
3   J004      机器学习实习生    某AI公司                 硕士  Python;机器学习;深度学习;TensorFlow或PyTorch                     0   北京    8000                   英语六级     参与机器学习模型训练和部署
4   J005    Java后端工程师  某金融科技公司                 本科         Java;Spring Boot;MySQL;Redis                     2   上海   15000                   英语四级        负责金融系统后端开发

--- 4. Resume dtypes ---
resume_id               str
name                    str
education               str
major                   str
skills                  str
experience_years      int64
city                    str
expected_salary       int64
certificates            str
project_experience      str
self_description        str
dtype: object

--- 4. Job dtypes ---
job_id                      str
job_title                   str
company                     str
required_education          str
required_skills             str
min_experience_years      int64
city                        str
salary                    int64
preferred_certificates      str
job_description             str
dtype: object

--- 5. Missing Values (Resumes) ---
education       1
city            1
certificates    3
dtype: int64

--- 5. Missing Values (Jobs) ---
company                   1
preferred_certificates    5
job_description           1
dtype: int64

--- 5b. Empty Strings (Resumes) ---

--- 5b. Empty Strings (Jobs) ---

--- 6. Duplicates ---
Resume duplicates: 0
Job duplicates:    0

--- 7. Education Distribution ---
education
本科     10
硕士      7
大专      2
NaN     1
Name: count, dtype: int64

--- 7. City Distribution (Resumes) ---
city
北京     4
南昌     3
深圳     3
上海     2
杭州     2
武汉     1
广州     1
成都     1
南京     1
NaN    1
厦门     1
Name: count, dtype: int64

--- 7. City Distribution (Jobs) ---
city
南昌    3
北京    3
上海    2
深圳    2
杭州    1
广州    1
Name: count, dtype: int64

--- 8. Skills Field Issues ---
  R018: skills field is EMPTY
  R019: double separator found -> excel;;hivesql

--- 9. Experience Years Distribution (Resumes) ---
count    20.000000
mean      0.600000
std       0.753937
min       0.000000
25%       0.000000
50%       0.000000
75%       1.000000
max       2.000000
Name: experience_years, dtype: float64

--- 9. Min Experience Distribution (Jobs) ---
count    12.000000
mean      0.666667
std       0.651339
min       0.000000
25%       0.000000
50%       1.000000
75%       1.000000
max       2.000000
Name: min_experience_years, dtype: float64

--- 10. Text Field Length Stats ---
resume self_description length: min=4, max=16, mean=8.8
resume project_experience length: min=8, max=29, mean=13.4
job job_description length: min=0, max=16, mean=12.3

--- 11. Salary Ranges ---
Resume expected_salary: min=5000, max=18000, mean=8025.0
Job salary: min=5000, max=15000, mean=9083.3
```
