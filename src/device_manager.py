"""设备数据管理与模拟"""
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from src.data_models import DeviceType, MetricType, HealthRecord
from src.database import db

class DeviceDataGenerator:
    """生成模拟的设备数据（用于演示和开发）"""

    @staticmethod
    def generate_heart_rate() -> float:
        return round(random.gauss(72, 10), 0)

    @staticmethod
    def generate_steps() -> int:
        return random.randint(3000, 15000)

    @staticmethod
    def generate_sleep_hours() -> float:
        return round(random.gauss(7.5, 1.0), 1)

    @staticmethod
    def generate_weight(base: float = 70.0) -> float:
        return round(base + random.gauss(0, 0.3), 1)

    @staticmethod
    def generate_body_fat() -> float:
        return round(random.uniform(15, 25), 1)

    @staticmethod
    def generate_blood_pressure() -> tuple:
        sys = round(random.gauss(115, 10), 0)
        dia = round(random.gauss(75, 8), 0)
        return sys, dia

    @staticmethod
    def generate_spo2() -> float:
        return round(random.gauss(98, 1), 0)

    @staticmethod
    def generate_calories() -> int:
        return random.randint(1500, 3000)

    @staticmethod
    def generate_stress_level() -> int:
        return random.randint(1, 10)

class DeviceSimulator:
    """设备模拟器，生成连续的健康数据流"""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self._running = False
        self._thread = None

    def start_simulation(self):
        """启动后台数据模拟（每60秒生成一次数据）"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._simulate_loop, daemon=True)
        self._thread.start()

    def stop_simulation(self):
        self._running = False

    def _simulate_loop(self):
        while self._running:
            self._generate_batch()
            time.sleep(60)

    def _generate_batch(self):
        now = datetime.now()
        gen = DeviceDataGenerator()

        # 心率（模拟手表，每5分钟一条，这里只演示1条）
        hr = gen.generate_heart_rate()
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="心率", value=hr,
            unit="次/分", recorded_at=now, device="智能手表"
        ))

        # 血氧
        spo2 = gen.generate_spo2()
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="血氧饱和度", value=spo2,
            unit="%", recorded_at=now, device="智能手表"
        ))

    def generate_daily_data(self, date: Optional[datetime] = None) -> int:
        """生成一天的数据记录，返回记录条数"""
        if date is None:
            date = datetime.now()
        base_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        gen = DeviceDataGenerator()
        count = 0

        # 全天心率（每30分钟一条）
        for hour in range(24):
            for minute in [0, 30]:
                t = base_date + timedelta(hours=hour, minutes=minute)
                hr = gen.generate_heart_rate()
                db.add_health_record(HealthRecord(
                    user_id=self.user_id, metric="心率", value=hr,
                    unit="次/分", recorded_at=t, device="智能手表"
                ))
                count += 1

        # 早晨起床血压
        sys, dia = gen.generate_blood_pressure()
        t = base_date + timedelta(hours=7, minutes=0)
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="收缩压", value=sys,
            unit="mmHg", recorded_at=t, device="血压计"
        ))
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="舒张压", value=dia,
            unit="mmHg", recorded_at=t, device="血压计"
        ))
        count += 2

        # 步数（晚上统计）
        steps = gen.generate_steps()
        t = base_date + timedelta(hours=22, minutes=0)
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="步数", value=steps,
            unit="步", recorded_at=t, device="手机"
        ))
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="消耗卡路里", value=gen.generate_calories(),
            unit="千卡", recorded_at=t, device="手机"
        ))
        count += 2

        # 睡眠数据
        sleep_hours = gen.generate_sleep_hours()
        t = base_date + timedelta(hours=8, minutes=0)
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="睡眠时长", value=sleep_hours,
            unit="小时", recorded_at=t, device="智能手表"
        ))
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="睡眠质量评分", value=random.randint(60, 95),
            unit="分", recorded_at=t, device="智能手表"
        ))
        count += 2

        # 早晨体重（智能秤）
        weight = gen.generate_weight(base=random.uniform(65, 75))
        t = base_date + timedelta(hours=7, minutes=5)
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="体重", value=weight,
            unit="kg", recorded_at=t, device="智能秤"
        ))
        bf = gen.generate_body_fat()
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="体脂率", value=bf,
            unit="%", recorded_at=t, device="智能秤"
        ))
        bmi = round(weight / ((random.uniform(1.65, 1.80) ** 2)), 1)
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="BMI", value=bmi,
            unit="", recorded_at=t, device="智能秤"
        ))
        count += 3

        # 压力水平
        t = base_date + timedelta(hours=20, minutes=0)
        db.add_health_record(HealthRecord(
            user_id=self.user_id, metric="压力水平", value=gen.generate_stress_level(),
            unit="分", recorded_at=t, device="手机"
        ))
        count += 1

        return count

    def generate_demo_data(self, days: int = 90):
        """生成多天的演示数据"""
        total = 0
        for i in range(days):
            d = datetime.now() - timedelta(days=days - 1 - i)
            total += self.generate_daily_data(d)
        return total

class DeviceConnector:
    """真实设备连接接口（预留，后续对接真实设备）"""

    def __init__(self):
        self.connected_devices: Dict[str, bool] = {}

    def connect_device(self, device_type: str) -> bool:
        self.connected_devices[device_type] = True
        return True

    def disconnect_device(self, device_type: str):
        self.connected_devices[device_type] = False

    def fetch_data(self, device_type: str) -> Optional[List[HealthRecord]]:
        if not self.connected_devices.get(device_type):
            return None

        gen = DeviceDataGenerator()
        now = datetime.now()
        records = []

        if device_type == "智能手表":
            records.append(HealthRecord(
                metric="心率", value=gen.generate_heart_rate(),
                unit="次/分", recorded_at=now, device="智能手表"
            ))
            records.append(HealthRecord(
                metric="血氧饱和度", value=gen.generate_spo2(),
                unit="%", recorded_at=now, device="智能手表"
            ))
        elif device_type == "智能秤":
            records.append(HealthRecord(
                metric="体重", value=gen.generate_weight(),
                unit="kg", recorded_at=now, device="智能秤"
            ))
        return records

device_simulator = DeviceSimulator()
device_connector = DeviceConnector()
