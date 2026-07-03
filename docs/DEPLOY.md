# HealthAgent 部署指南 - GitHub + Streamlit Cloud

## 第一步：安装 Git
1. 打开 https://git-scm.com/download/win
2. 下载安装包并安装
3. 安装后打开 cmd 或 PowerShell，输入 git --version
4. 显示版本号即成功

## 第二步：创建 GitHub 仓库
1. 打开 https://github.com 注册/登录账号
2. 点 "+" → "New repository"
3. 仓库名填 health-agent，选 Private，点 Create
4. 复制页面上的仓库地址（git remote ...那一行）

## 第三步：上传代码
打开 cmd，逐条执行：

cd C:\Users\ASUS\Documents\课题规划\health-agent
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/health-agent.git
git branch -M main
git push -u origin main

## 第四步：部署到 Streamlit Cloud
1. 打开 https://share.streamlit.io
2. 用 GitHub 登录，点 "New app"
3. 选 health-agent 仓库
4. Branch: main, Main file: app.py
5. 点 Deploy

## 第五步：配置 API Key（关键！）
1. 部署完成后进 app 设置 → Secrets
2. 填入：
LLM_API_KEY = "sk-ayZExNNKfTe8Awi4mGJ7Rg"
LLM_BASE_URL = "https://api.llm.ustc.edu.cn/v1"
LLM_MODEL = "qwen3.5"
3. 保存，应用自动重启

## 第六步：获得分享链接
地址格式：https://你的用户名-health-agent.streamlit.app
