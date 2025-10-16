import enum
from sqlalchemy import (Column, Integer, String, BigInteger, Enum, Boolean)
from database.engine import Base

class PlanCategory(enum.Enum):
    NORMAL = "عادی"
    SPECIAL = "ویژه"
    GAMING = "گیمینگ"
    TRADE = "ترید"

class Plan(Base):
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum(PlanCategory), nullable=False, default=PlanCategory.NORMAL)
    duration_days = Column(Integer, nullable=False)
    traffic_gb = Column(Integer, nullable=False, default=0)
    price = Column(BigInteger, nullable=False)
    device_limit = Column(Integer, nullable=False, default=1)
    
    # ---> فیلد جدید <---
    # مشخص می‌کند که آیا این پلن، پلن ویژه اکانت تست است یا خیر
    is_test_plan = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<Plan(name='{self.name}', price={self.price})>"