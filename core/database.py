from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .config import settings

# Database engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Session factory
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    department = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    manager_id = Column(String(255), nullable=True)
    start_date = Column(DateTime, nullable=False)
    access_level = Column(String(100), nullable=False)
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BehavioralProfile(Base):
    __tablename__ = "behavioral_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False)
    profile_data = Column(JSON, nullable=False)
    baseline_established = Column(Boolean, default=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)

class ThreatAlert(Base):
    __tablename__ = "threat_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False)
    threat_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)
    status = Column(String(50), default="open")
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, nullable=True)
    false_positive = Column(Boolean, default=False)
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DataEvent(Base):
    __tablename__ = "data_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), ForeignKey("users.user_id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    source_ip = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    event_data = Column(JSON, nullable=False)
    risk_score = Column(Float, default=0.0)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    model_type = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    model_path = Column(String(500), nullable=False)
    performance_metrics = Column(JSON, nullable=True)
    training_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True)
    action = Column(String(255), nullable=False)
    resource = Column(String(255), nullable=False)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database connection functions
async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

class Database:
    def __init__(self):
        self.engine = engine
        self.session = async_session

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self):
        async with self.session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
