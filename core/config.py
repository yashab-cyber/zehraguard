from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "ZehraGuard InsightX"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database Configuration
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "zehraguard"
    postgres_user: str = "zehraguard"
    postgres_password: str = "secure_password_123"
    
    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: str = "redis_password_123"
    redis_db: int = 0
    
    # InfluxDB Configuration
    influxdb_url: str = "http://influxdb:8086"
    influxdb_token: str = "zehraguard-super-secret-auth-token"
    influxdb_org: str = "zehraguard"
    influxdb_bucket: str = "behavioral_data"
    
    # RabbitMQ Configuration
    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "zehraguard"
    rabbitmq_password: str = "rabbitmq_password_123"
    
    # ML Configuration
    ml_model_path: str = "/app/models"
    ml_training_data_path: str = "/app/data"
    anomaly_threshold: float = 0.8
    risk_score_threshold: float = 0.7
    
    # Alert Configuration
    alert_cooldown_minutes: int = 15
    max_alerts_per_user_per_hour: int = 10
    
    # SIEM Integration
    splunk_host: Optional[str] = None
    splunk_port: Optional[int] = 8088
    splunk_token: Optional[str] = None
    
    azure_sentinel_workspace_id: Optional[str] = None
    azure_sentinel_shared_key: Optional[str] = None
    
    # Compliance & Privacy
    data_retention_days: int = 90
    encryption_key: Optional[str] = None
    gdpr_compliance: bool = True
    
    # Monitoring
    prometheus_enabled: bool = True
    prometheus_port: int = 9090
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def rabbitmq_url(self) -> str:
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
