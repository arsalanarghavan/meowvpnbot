from datetime import datetime
from sqlalchemy import (Column, Integer, String, BigInteger, DateTime, 
                        Boolean, ForeignKey)
from sqlalchemy.orm import relationship

from database.engine import Base

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey('plans.id'), nullable=False)
    
    # This username is now shared across ALL panels for this service
    username_in_panel = Column(String(100), nullable=False, unique=True)
    
    note = Column(String(100), nullable=True)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expire_date = Column(DateTime, nullable=False)
    auto_renew = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)

    user = relationship("User")
    plan = relationship("Plan")