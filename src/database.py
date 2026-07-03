"""数据库管理"""
import sqlite3
import json
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from src.config import config
from src.data_models import (
    HealthRecord, LabReport, Symptom, Medication,
    Diagnosis, HealthPlan, HealthAnalysis, UserProfile
)

class Database:
    def __init__(self):
        self.db_path = config.DB_PATH
        self._init_db()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        c = conn.cursor()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT DEFAULT '',
                recorded_at TIMESTAMP NOT NULL,
                device TEXT DEFAULT '手动录入',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS lab_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                report_name TEXT NOT NULL,
                report_date DATE NOT NULL,
                hospital TEXT,
                items TEXT,
                summary TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                symptom_name TEXT NOT NULL,
                severity INTEGER DEFAULT 1,
                body_part TEXT,
                description TEXT,
                started_at TIMESTAMP NOT NULL,
                ended_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                medication_name TEXT NOT NULL,
                dosage TEXT,
                frequency TEXT,
                start_date DATE NOT NULL,
                end_date DATE,
                prescribed_by TEXT,
                reason TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                diagnosis_name TEXT NOT NULL,
                diagnosis_date DATE NOT NULL,
                doctor TEXT,
                hospital TEXT,
                status TEXT DEFAULT '随访中',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS health_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                plan_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                priority TEXT DEFAULT '中',
                due_date DATE,
                is_completed INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS health_analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                analysis_type TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                risk_findings TEXT,
                recommendations TEXT,
                related_period TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY DEFAULT 'default',
                name TEXT,
                age INTEGER,
                gender TEXT,
                height REAL,
                weight REAL,
                medical_history TEXT DEFAULT '',
                allergies TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        conn.close()

    # ---- 健康记录 ----
    def add_health_record(self, record: HealthRecord) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO health_records (user_id, metric, value, unit, recorded_at, device, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (record.user_id, record.metric, record.value, record.unit,
              record.recorded_at, record.device, record.notes))
        conn.commit()
        rid = c.lastrowid
        conn.close()
        return rid

    def get_health_records(self, metric: str = None, days: int = 30, user_id: str = "default") -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        if metric:
            c.execute("""
                SELECT * FROM health_records
                WHERE user_id=? AND metric=? AND recorded_at >= datetime('now', ?)
                ORDER BY recorded_at DESC
            """, (user_id, metric, f'-{days} days'))
        else:
            c.execute("""
                SELECT * FROM health_records
                WHERE user_id=? AND recorded_at >= datetime('now', ?)
                ORDER BY recorded_at DESC
            """, (user_id, f'-{days} days'))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    def get_latest_values(self, user_id: str = "default") -> Dict:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT metric, value, unit, recorded_at FROM health_records
            WHERE user_id=? AND recorded_at >= datetime('now', '-7 days')
            GROUP BY metric HAVING MAX(recorded_at)
        """, (user_id,))
        result = {}
        for r in c.fetchall():
            result[r[0]] = {"value": r[1], "unit": r[2], "time": r[3]}
        conn.close()
        return result

    # ---- 检验报告 ----
    def add_lab_report(self, report: LabReport) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO lab_reports (user_id, report_name, report_date, hospital, items, summary, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (report.user_id, report.report_name, report.report_date,
              report.hospital, json.dumps(report.items, ensure_ascii=False),
              report.summary, report.file_path))
        conn.commit()
        rid = c.lastrowid
        conn.close()
        return rid

    def get_lab_reports(self, user_id: str = "default") -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM lab_reports WHERE user_id=? ORDER BY report_date DESC
        """, (user_id,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ---- 症状 ----
    def add_symptom(self, symptom: Symptom) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO symptoms (user_id, symptom_name, severity, body_part, description, started_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (symptom.user_id, symptom.symptom_name, symptom.severity,
              symptom.body_part, symptom.description, symptom.started_at, symptom.is_active))
        conn.commit()
        rid = c.lastrowid
        conn.close()
        return rid

    def get_active_symptoms(self, user_id: str = "default") -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM symptoms WHERE user_id=? AND is_active=1 ORDER BY severity DESC
        """, (user_id,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ---- 用药 ----
    def add_medication(self, med: Medication) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO medications (user_id, medication_name, dosage, frequency, start_date, end_date, prescribed_by, reason, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (med.user_id, med.medication_name, med.dosage, med.frequency,
              med.start_date, med.end_date, med.prescribed_by, med.reason, med.is_active))
        conn.commit()
        rid = c.lastrowid
        conn.close()
        return rid

    def get_active_medications(self, user_id: str = "default") -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM medications WHERE user_id=? AND is_active=1 ORDER BY start_date DESC
        """, (user_id,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ---- 诊断 ----
    def add_diagnosis(self, diag: Diagnosis) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO diagnoses (user_id, diagnosis_name, diagnosis_date, doctor, hospital, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (diag.user_id, diag.diagnosis_name, diag.diagnosis_date,
              diag.doctor, diag.hospital, diag.status, diag.notes))
        conn.commit()
        rid = c.lastrowid
        conn.close()
        return rid

    def get_diagnoses(self, user_id: str = "default") -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM diagnoses WHERE user_id=? ORDER BY diagnosis_date DESC
        """, (user_id,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ---- 健康分析 ----
    def save_analysis(self, analysis: HealthAnalysis) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO health_analyses (user_id, analysis_type, title, summary, risk_findings, recommendations, related_period)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (analysis.user_id, analysis.analysis_type, analysis.title,
              analysis.summary, analysis.risk_findings, analysis.recommendations,
              analysis.related_period))
        conn.commit()
        rid = c.lastrowid
        conn.close()
        return rid

    def get_analyses(self, user_id: str = "default", limit: int = 10) -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM health_analyses WHERE user_id=? ORDER BY created_at DESC LIMIT ?
        """, (user_id, limit))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ---- 健康计划 ----
    def save_plan(self, plan: HealthPlan) -> int:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO health_plans (user_id, plan_type, title, content, priority, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (plan.user_id, plan.plan_type, plan.title, plan.content, plan.priority, plan.due_date))
        conn.commit()
        rid = c.lastrowid
        conn.close()
        return rid

    def get_active_plans(self, user_id: str = "default") -> List[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT * FROM health_plans WHERE user_id=? AND is_completed=0 ORDER BY priority DESC
        """, (user_id,))
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        return rows

    # ---- 用户资料 ----
    def get_user_profile(self, user_id: str = "default") -> Optional[Dict]:
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM user_profiles WHERE user_id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None

    def save_user_profile(self, profile: UserProfile):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO user_profiles (user_id, name, age, gender, height, weight, medical_history, allergies, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (profile.user_id, profile.name, profile.age, profile.gender,
              profile.height, profile.weight, profile.medical_history, profile.allergies))
        conn.commit()
        conn.close()

db = Database()
