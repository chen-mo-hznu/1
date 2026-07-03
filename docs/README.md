# HealthAgent - 个人健康智能体
## 项目简介
HealthAgent 是一个基于大语言模型的个人健康智能体系统，整合智能手表、智能秤、手机等多设备数据，提供全天候个性化健康分析与指导。
## 系统架构
- 智能设备 -> 数据采集层 -> 数据标准化 -> 个人健康数据库
- 个人健康数据库 + 医学知识库 -> LLM推理引擎
- 输出: 健康分析报告 / 个性化建议 / 风险预警
## 功能特性
1. 多设备数据整合：手表(心率/血氧/睡眠)、秤(体重/体脂)、手机(步数/压力)
2. AI智能分析：指标解读、综合评估、周报日报、报告解读、医学问答
3. 个人健康档案：长期追踪、趋势分析、个性化方案
## 技术栈
前端: Streamlit | 后端: Python | LLM: 智谱AI/OpenAI | RAG: LangChain+FAISS | 存储: SQLite | 可视化: Plotly
## 快速开始
1. 安装Python 3.10+
2. 注册智谱AI (open.bigmodel.cn)，获取API Key填入.env
3. pip install -r requirements.txt
4. streamlit run app.py
## 项目结构
health-agent/  app.py / src/ (config, data_models, database, device_manager, agent, knowledge_base, prompts) / data/ / docs/
## 参赛价值
- 主题契合：算力+智能体
- 创新性：个人健康数字孪生
- 创业潜力：万亿级健康管理市场
- 临床背景优势
- 可演示性强
## 商业化路径
- 个人健康订阅 / 企业员工健康管理 / 体检中心合作 / 保险增值服务
## License: MIT
