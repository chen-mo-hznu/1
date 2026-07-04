# 如何推送到 GitHub

由于当前网络无法直连 GitHub，请按以下步骤操作：

## 方法一：手机热点（推荐）
1. 手机开热点，电脑连接手机网络
2. 打开 cmd 执行：

cd C:\Users\ASUS\Documents\课题规划\health-agent
git push -u origin master

## 方法二：学校机房
在能访问 GitHub 的电脑上操作即可

## 方法三：直接下载
把 health-agent 文件夹整个拷贝到能上网的电脑上操作

## 然后部署到 Streamlit Cloud
1. go to https://share.streamlit.io
2. 用 GitHub 登录，点 New app
3. 选择 health-agent 仓库
4. Branch: master, Main file: app.py
5. 点 Deploy
