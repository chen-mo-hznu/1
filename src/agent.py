import json
from datetime import datetime
from src.config import config
from src.prompts import *
from src.database import db
from src.knowledge_base import knowledge_base

class HealthAgent:
    def __init__(self):
        self._llm = None
        self.conversation_history = []

    def _get_llm(self):
        if self._llm is None:
            try:
                from openai import OpenAI
                self._llm = OpenAI(api_key=config.LLM_API_KEY, base_url=config.LLM_BASE_URL)
            except Exception as e:
                print(f"LLM init error: {e}")
        return self._llm

    def _tools(self):
        return [{"type":"function","function":{"name":"get_vital_signs","description":"获取用户最新生命体征数据","parameters":{"type":"object","properties":{},"required":[]}}},
{"type":"function","function":{"name":"get_metric_trend","description":"获取某个指标趋势","parameters":{"type":"object","properties":{"metric":{"type":"string","description":"指标名称"},"days":{"type":"integer","description":"天数"}},"required":["metric","days"]}}},
{"type":"function","function":{"name":"check_anomalies","description":"检查近期所有指标的异常情况","parameters":{"type":"object","properties":{},"required":[]}}},
{"type":"function","function":{"name":"search_medical","description":"查询医学知识","parameters":{"type":"object","properties":{"question":{"type":"string","description":"问题"}},"required":["question"]}}},
{"type":"function","function":{"name":"get_user_profile","description":"获取用户档案","parameters":{"type":"object","properties":{},"required":[]}}},
{"type":"function","function":{"name":"get_symptoms","description":"获取当前症状","parameters":{"type":"object","properties":{},"required":[]}}}]

    def _run_tool(self, name, args):
        m = {"get_vital_signs":self._vitals,"get_metric_trend":self._trend,"check_anomalies":self._anomalies,"search_medical":self._search,"get_user_profile":self._profile,"get_symptoms":self._symptoms}
        f = m.get(name)
        if not f: return '{"error":"unknown tool"}'
        try: return json.dumps(f(**args) if args else f(), ensure_ascii=False, default=str)
        except Exception as e: return json.dumps({"error":str(e)})

    def _vitals(self):
        return {"vitals":db.get_latest_values()}

    def _trend(self, metric, days=7):
        r = db.get_health_records(metric=metric, days=days)
        if not r: return {"metric":metric,"data":[]}
        v = [x["value"] for x in r]
        return {"metric":metric,"avg":round(sum(v)/len(v),1),"min":min(v),"max":max(v),"count":len(v)}

    def _anomalies(self):
        from src.data_models import REFERENCE_RANGES
        r = db.get_health_records(days=7)
        latest = {}
        for x in r:
            m = x["metric"]
            if m not in latest: latest[m] = x["value"]
        ans = []
        for k,v in latest.items():
            ref = REFERENCE_RANGES.get(k)
            if ref and (v < ref["warn_low"] or v > ref["warn_high"]):
                ans.append({"metric":k,"value":v,"unit":ref["unit"],"status":"异常"})
        return {"anomalies":ans}

    def _search(self, question):
        return {"knowledge":knowledge_base.load_guideline_text()[:2000]}

    def _profile(self):
        p = db.get_user_profile()
        return {"profile":p} if p else {}

    def _symptoms(self):
        return {"symptoms":db.get_active_symptoms()}

    def chat(self, msg):
        llm = self._get_llm()
        if not llm: return "请先配置API Key"
        sys = "你是个人健康智能体。你可以用工具获取用户数据并分析。发现异常要提醒。给出具体建议。不替代医生诊断。"
        messages = [{"role":"system","content":sys}]
        for h in self.conversation_history[-8:]: messages.append(h)
        messages.append({"role":"user","content":msg})
        for _ in range(5):
            try:
                resp = llm.chat.completions.create(model=config.LLM_MODEL,messages=messages,tools=self._tools(),temperature=0.3,max_tokens=1500)
                m = resp.choices[0].message
                if m.tool_calls:
                    messages.append(m)
                    for tc in m.tool_calls:
                        args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                        result = self._run_tool(tc.function.name, args)
                        messages.append({"role":"tool","tool_call_id":tc.id,"content":result})
                else:
                    self.conversation_history.append({"role":"user","content":msg})
                    self.conversation_history.append({"role":"assistant","content":m.content})
                    return m.content
            except Exception as e:
                return f"出错: {str(e)}"
        return "请再说具体些"

    def comprehensive_analysis(self): return self.chat("全面分析我近期的健康数据")
    def generate_weekly_report(self): return self.chat("生成本周健康总结")
    def generate_daily_advice(self): return self.chat("根据今日数据给出日常建议")
    def chat_with_knowledge(self, q): return self.chat(q)
    def clear_history(self): self.conversation_history = []

health_agent = HealthAgent()
