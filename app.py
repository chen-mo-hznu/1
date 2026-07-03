import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
from src.database import db
from src.data_models import *
from src.device_manager import device_simulator
from src.agent import health_agent
from src.knowledge_base import knowledge_base
st.set_page_config(page_title="HealthAgent", page_icon=":hospital:", layout="wide")
if "init" not in st.session_state:
    knowledge_base.initialize()
    st.session_state.init = True
st.sidebar.title("HealthAgent")
st.sidebar.caption("个人健康智能体")
page = st.sidebar.radio("导航", ["智能体对话", "健康仪表盘", "数据录入", "设备数据", "AI健康分析", "检验报告", "医学知识库", "个人档案"])

if page == "智能体对话":
    st.title("个人健康智能体")
    st.caption("与你的 AI 健康助手对话，它可以查询你的健康数据、分析指标趋势、发现异常并给出建议")
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [{"role": "assistant", "content": "你好！我是你的个人健康智能体。我可以帮你查看健康数据、分析指标、检查异常。请问有什么可以帮你的？"}]
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if prompt := st.chat_input("问你的健康助手..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.status("智能体正在思考，调用工具分析数据...", expanded=True) as status:
                st.write("Connecting to LLM...")
                response = health_agent.chat(prompt)
                st.write("Analysis complete")
            st.markdown(response)
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    if st.button("清空对话"):
        health_agent.clear_history()
        st.session_state.chat_messages = []
        st.rerun()

elif page == "健康仪表盘":
    st.title("健康仪表盘")
    col1, col2, col3, col4 = st.columns(4)
    latest = db.get_latest_values()
    display_metrics = {"心率": ("heart", "次/分", 72), "血氧饱和度": ("blood", "%", 98), "睡眠时长": ("moon", "小时", 7.5), "步数": ("footprints", "步", 8000)}
    for (m, (icon, unit, default)), col in zip(display_metrics.items(), [col1, col2, col3, col4]):
        v = latest.get(m, {}).get("value", default)
        col.metric(label=m, value=f"{v}{unit}")
    st.subheader("近期数据趋势")
    records = db.get_health_records(days=14)
    if records:
        df = pd.DataFrame(records)
        df["recorded_at"] = pd.to_datetime(df["recorded_at"])
        metrics_to_show = ["心率", "血氧饱和度", "睡眠时长", "体重"]
        tabs = st.tabs(metrics_to_show)
        for ti, mt in enumerate(metrics_to_show):
            with tabs[ti]:
                mdf = df[df["metric"] == mt].copy()
                if not mdf.empty:
                    mdf = mdf.sort_values("recorded_at")
                    fig = px.line(mdf, x="recorded_at", y="value", title=f"{mt}趋势")
                    fig.update_layout(height=300)
                    st.plotly_chart(fig, width='stretch')
                else:
                    st.info(f"暂无{mt}数据")
    else:
        st.info("暂无数据，请在「数据录入」页面录入或生成模拟数据。")

elif page == "数据录入":
    st.title("健康数据录入")
    tab1, tab2, tab3, tab4 = st.tabs(["指标记录", "症状记录", "用药记录", "诊断记录"])
    with tab1:
        with st.form("record_form"):
            col1, col2 = st.columns(2)
            metric_options = [m.value for m in MetricType]
            with col1: metric = st.selectbox("指标", metric_options)
            with col2: value = st.number_input("数值", step=0.1)
            col3, col4 = st.columns(2)
            with col3: device = st.selectbox("设备来源", ["手动录入", "智能手表", "智能秤", "血压计", "血糖仪", "手机"])
            with col4: notes = st.text_input("备注")
            if st.form_submit_button("保存记录"):
                r = HealthRecord(metric=metric, value=value, unit="", recorded_at=datetime.now(), device=device, notes=notes)
                db.add_health_record(r)
                st.success("记录已保存")
    with tab2:
        with st.form("symptom_form"):
            col1, col2 = st.columns(2)
            with col1: name = st.text_input("症状名称")
            with col2: severity = st.slider("严重程度", 1, 10, 5)
            col3, col4 = st.columns(2)
            with col3: body_part = st.text_input("部位")
            with col4: desc = st.text_area("描述")
            if st.form_submit_button("记录症状"):
                s = Symptom(symptom_name=name, severity=severity, body_part=body_part, description=desc, started_at=datetime.now())
                db.add_symptom(s)
                st.success("症状已记录")
    with tab3:
        with st.form("med_form"):
            col1, col2 = st.columns(2)
            with col1: med_name = st.text_input("药品名称")
            with col2: dosage = st.text_input("剂量")
            col3, col4 = st.columns(2)
            with col3: freq = st.text_input("频率")
            with col4: reason = st.text_input("用药原因")
            if st.form_submit_button("记录用药"):
                m = Medication(medication_name=med_name, dosage=dosage, frequency=freq, start_date=date.today(), reason=reason)
                db.add_medication(m)
                st.success("用药已记录")
    with tab4:
        with st.form("diag_form"):
            col1, col2 = st.columns(2)
            with col1: diag_name = st.text_input("诊断名称")
            with col2: diag_date = st.date_input("诊断日期", date.today())
            col3, col4 = st.columns(2)
            with col3: doctor = st.text_input("诊断医生")
            with col4: hospital = st.text_input("医院")
            status = st.selectbox("状态", ["已治愈", "随访中", "慢性"])
            if st.form_submit_button("记录诊断"):
                d = Diagnosis(diagnosis_name=diag_name, diagnosis_date=diag_date, doctor=doctor, hospital=hospital, status=status)
                db.add_diagnosis(d)
                st.success("诊断已记录")
    st.divider()
    if st.button("生成7天模拟数据"):
        n = device_simulator.generate_demo_data(7)
        st.success(f"已生成{n}条模拟数据，刷新后可在仪表盘查看")
        st.rerun()

elif page == "设备数据":
    st.title("设备数据管理")
    st.info("此处展示来自不同设备的健康数据流。实际部署时可对接智能手表、智能秤等蓝牙/WiFi设备。")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("已接入设备")
        devices = [("智能手表", "在线", "心率、血氧、睡眠、运动"), ("智能秤", "在线", "体重、体脂、BMI"), ("手机", "在线", "步数、卡路里、压力"), ("血压计", "未连接", "收缩压、舒张压")]
        for name, status, metric_list in devices:
            with st.container(border=True):
                st.markdown(f"**{name}** - {status}")
                st.caption(f"监测指标：{metric_list}")
    with col2:
        st.subheader("实时数据")
        latest_data = db.get_latest_values()
        for metric_name, info_item in latest_data.items():
            st.markdown(f"{metric_name}：**{info_item['value']}** {info_item['unit']}")
    st.subheader("设备数据流（近7天）")
    recent_records = db.get_health_records(days=7)
    if recent_records:
        df = pd.DataFrame(recent_records)
        df["recorded_at"] = pd.to_datetime(df["recorded_at"])
        df["date"] = df["recorded_at"].dt.date
        device_counts = df.groupby(["date", "device"]).size().reset_index(name="记录数")
        if not device_counts.empty:
            fig = px.bar(device_counts, x="date", y="记录数", color="device", title="各设备数据采集情况")
            st.plotly_chart(fig, width='stretch')

elif page == "AI健康分析":
    st.title("AI健康分析")
    st.info("如需自由对话，请使用「智能体对话」页面")
    tab1, tab2, tab3 = st.tabs(["综合健康分析", "本周总结", "今日建议"])
    with tab1:
        if st.button("生成全面健康分析报告"):
            with st.spinner("AI正在分析您的健康数据..."):
                result = health_agent.comprehensive_analysis()
                st.markdown(result)
    with tab2:
        if st.button("生成本周健康总结"):
            with st.spinner("生成中..."):
                result = health_agent.generate_weekly_report()
                st.markdown(result)
    with tab3:
        if st.button("获取今日健康建议"):
            with st.spinner("生成中..."):
                result = health_agent.generate_daily_advice()
                st.markdown(result)

elif page == "检验报告":
    st.title("检验报告分析")
    input_method = st.radio("输入方式", ["手动输入检验项目", "查看历史报告"])
    if input_method == "手动输入检验项目":
        with st.form("lab_report_form"):
            rname = st.text_input("报告名称", "2024年度体检报告")
            rdate = st.date_input("报告日期", date.today())
            st.markdown("输入检验项目（每行一个，格式：项目名 数值 单位 范围）")
            items_text = st.text_area("检验项目", height=150)
            if st.form_submit_button("AI解读报告"):
                if items_text:
                    with st.spinner("AI正在分析..."):
                        analysis = health_agent.analyze_lab_report(rname, str(rdate), items_text)
                        st.markdown("### AI分析结果")
                        st.markdown(analysis)
                        report = LabReport(report_name=rname, report_date=rdate, items=[{"raw": items_text}], summary=analysis)
                        db.add_lab_report(report)
    else:
        reports = db.get_lab_reports()
        if reports:
            for r in reports[-5:]:
                with st.container(border=True):
                    st.markdown(f"**{r['report_name']}** ({r['report_date']})")
                    if r.get('summary'):
                        st.markdown(r['summary'][:200] + "...")
        else:
            st.info("暂无历史报告")

elif page == "医学知识库":
    st.title("医学知识库")
    st.info("知识库基于临床指南和医学教材构建。你可以上传医学文档（.md或.txt格式）到 data/medical_knowledge/ 目录来扩充知识库。")
    st.markdown("### 内置参考指南摘要")
    st.markdown(knowledge_base.load_guideline_text())

elif page == "个人档案":
    st.title("个人健康档案")
    profile = db.get_user_profile()
    with st.form("profile_form"):
        cols = st.columns(3)
        with cols[0]:
            uname = st.text_input("姓名", profile.get("name", "") if profile else "")
            uage = st.number_input("年龄", value=profile.get("age", 30) if profile else 30)
            ugender = st.selectbox("性别", ["男", "女"], index=0 if not profile or profile.get("gender")=="男" else 1)
        with cols[1]:
            uheight = st.number_input("身高(cm)", value=float(profile.get("height", 170)) if profile else 170.0)
            uweight = st.number_input("体重(kg)", value=float(profile.get("weight", 65)) if profile else 65.0)
        with cols[2]:
            umedical = st.text_area("既往病史", profile.get("medical_history", "") if profile else "", height=80)
            uallergies = st.text_area("过敏史", profile.get("allergies", "") if profile else "", height=80)
        if st.form_submit_button("保存档案"):
            p = UserProfile(name=uname, age=uage, gender=ugender, height=uheight, weight=uweight, medical_history=umedical, allergies=uallergies)
            db.save_user_profile(p)
            st.success("个人档案已保存")
    if profile:
        bmi = profile.get("weight", 0) / ((profile.get("height", 170)/100)**2) if profile.get("height") else 0
        if bmi > 0:
            st.metric("BMI", f"{bmi:.1f}")
    st.subheader("统计数据")
    all_records = db.get_health_records(days=365)
    if all_records:
        st.metric("总记录数", len(all_records))
        tracked_metrics = len(set(r["metric"] for r in all_records))
        st.metric("监测指标种类", tracked_metrics)
    if st.button("清除所有数据"):
        import os
        db_path = "data/user_data/health.db"
        if os.path.exists(db_path):
            os.remove(db_path)
        st.rerun()
st.sidebar.divider()
st.sidebar.caption("HealthAgent v2.0 | 个人健康智能体")
st.sidebar.caption("适用：107杯算力与智能体开发大赛")
