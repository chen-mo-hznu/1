"""健康数据模型定义"""
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum

class DeviceType(Enum):
    SMART_WATCH = "智能手表"
    SMART_SCALE = "智能秤"
    PHONE = "手机"
    BLOOD_PRESSURE_MONITOR = "血压计"
    BLOOD_GLUCOSE_METER = "血糖仪"
    MANUAL = "手动录入"

class MetricType(Enum):
    # 生命体征
    HEART_RATE = "心率"
    BLOOD_PRESSURE_SYS = "收缩压"
    BLOOD_PRESSURE_DIA = "舒张压"
    SPO2 = "血氧饱和度"
    BODY_TEMPERATURE = "体温"
    RESPIRATORY_RATE = "呼吸频率"

    # 身体成分
    WEIGHT = "体重"
    BMI = "BMI"
    BODY_FAT = "体脂率"
    MUSCLE_MASS = "肌肉量"
    BONE_MASS = "骨量"
    BODY_WATER = "水分率"

    # 活动与代谢
    STEPS = "步数"
    CALORIES = "消耗卡路里"
    ACTIVE_MINUTES = "活跃分钟数"

    # 睡眠
    SLEEP_DURATION = "睡眠时长"
    DEEP_SLEEP = "深睡时长"
    LIGHT_SLEEP = "浅睡时长"
    REM_SLEEP = "REM睡眠"
    SLEEP_QUALITY = "睡眠质量评分"

    # 生化指标
    BLOOD_GLUCOSE = "血糖"
    TOTAL_CHOLESTEROL = "总胆固醇"
    LDL = "低密度脂蛋白"
    HDL = "高密度脂蛋白"
    TRIGLYCERIDES = "甘油三酯"
    HBA1C = "糖化血红蛋白"

    # 情绪与主观感受
    STRESS_LEVEL = "压力水平"
    MOOD_SCORE = "情绪评分"
    ENERGY_LEVEL = "精力水平"

@dataclass
class HealthRecord:
    """单条健康记录"""
    id: Optional[int] = None
    user_id: str = "default"
    metric: str = ""  # MetricType value
    value: float = 0.0
    unit: str = ""
    recorded_at: datetime = field(default_factory=datetime.now)
    device: str = "手动录入"
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class LabReport:
    """检验报告"""
    id: Optional[int] = None
    user_id: str = "default"
    report_name: str = ""
    report_date: date = field(default_factory=date.today)
    hospital: Optional[str] = None
    items: List[Dict] = field(default_factory=list)
    summary: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Symptom:
    """症状记录"""
    id: Optional[int] = None
    user_id: str = "default"
    symptom_name: str = ""
    severity: int = 1  # 1-10
    body_part: Optional[str] = None
    description: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Medication:
    """用药记录"""
    id: Optional[int] = None
    user_id: str = "default"
    medication_name: str = ""
    dosage: str = ""
    frequency: str = ""
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None
    prescribed_by: Optional[str] = None
    reason: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class Diagnosis:
    """诊断记录"""
    id: Optional[int] = None
    user_id: str = "default"
    diagnosis_name: str = ""
    diagnosis_date: date = field(default_factory=date.today)
    doctor: Optional[str] = None
    hospital: Optional[str] = None
    status: str = "随访中"  # 已治愈/随访中/慢性
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class HealthPlan:
    """AI生成健康计划"""
    id: Optional[int] = None
    user_id: str = "default"
    plan_type: str = ""  # 饮食/运动/用药/复查
    title: str = ""
    content: str = ""
    priority: str = "中"
    due_date: Optional[date] = None
    is_completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class HealthAnalysis:
    """AI分析结果"""
    id: Optional[int] = None
    user_id: str = "default"
    analysis_type: str = ""  # 日常/周报/月报/报告解读
    title: str = ""
    summary: str = ""
    risk_findings: str = ""
    recommendations: str = ""
    related_period: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class UserProfile:
    """用户基本资料"""
    user_id: str = "default"
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    medical_history: str = ""
    allergies: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

# 指标参考范围
REFERENCE_RANGES = {
    "心率": {"unit": "次/分", "min": 60, "max": 100, "warn_low": 50, "warn_high": 120},
    "收缩压": {"unit": "mmHg", "min": 90, "max": 120, "warn_low": 80, "warn_high": 140},
    "舒张压": {"unit": "mmHg", "min": 60, "max": 80, "warn_low": 50, "warn_high": 90},
    "血氧饱和度": {"unit": "%", "min": 95, "max": 100, "warn_low": 90, "warn_high": 100},
    "体温": {"unit": "C", "min": 36.0, "max": 37.3, "warn_low": 35.5, "warn_high": 38.0},
    "BMI": {"unit": "", "min": 18.5, "max": 24.0, "warn_low": 17.0, "warn_high": 28.0},
    "体脂率": {"unit": "%", "min": 10, "max": 20, "warn_low": 5, "warn_high": 30},
    "血糖": {"unit": "mmol/L", "min": 3.9, "max": 6.1, "warn_low": 3.0, "warn_high": 7.0},
    "总胆固醇": {"unit": "mmol/L", "min": 2.8, "max": 5.2, "warn_low": 2.0, "warn_high": 6.2},
    "糖化血红蛋白": {"unit": "%", "min": 4.0, "max": 6.0, "warn_low": 3.5, "warn_high": 7.0},
}
