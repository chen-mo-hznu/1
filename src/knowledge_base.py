"""医学知识库（简化版，无需外部依赖）"""
import os
from typing import List
from src.config import config

class MedicalKnowledgeBase:
    def __init__(self):
        self.knowledge_dir = config.KNOWLEDGE_DIR
        self._initialized = True

    def is_ready(self) -> bool:
        return True

    def initialize(self):
        self._initialized = True

    def query(self, question: str) -> List[str]:
        return []

    def load_guideline_text(self) -> str:
        return """
## 常见临床指标参考

### 心血管系统
- 正常血压：收缩压 90-120mmHg，舒张压 60-80mmHg
- 正常心率：60-100次/分
- 正常血氧饱和度：95%-100%

### 代谢指标
- 空腹血糖正常值：3.9-6.1 mmol/L
- 糖化血红蛋白正常值：4.0%-6.0%
- 总胆固醇正常值：2.8-5.2 mmol/L
- 低密度脂蛋白正常值：<3.4 mmol/L
- 高密度脂蛋白正常值：>1.0 mmol/L

### 身体成分
- 健康BMI范围：18.5-24.0
- 健康体脂率：男性10-20%，女性18-28%

### 睡眠建议
- 成人推荐睡眠时长：7-9小时
- 深睡占比建议：20-25%

### 运动建议
- 成人每周至少150分钟中等强度有氧运动
- 每日步数建议：6000-10000步
"""

knowledge_base = MedicalKnowledgeBase()
