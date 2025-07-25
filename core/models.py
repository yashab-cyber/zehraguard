from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import uuid

class DataType(str, Enum):
    KEYSTROKE = "keystroke"
    MOUSE_MOVEMENT = "mouse_movement"
    FILE_ACCESS = "file_access"
    NETWORK_REQUEST = "network_request"
    LOGIN_EVENT = "login_event"
    APPLICATION_USAGE = "application_usage"
    SYSTEM_COMMAND = "system_command"

class ThreatType(str, Enum):
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_TRADING = "insider_trading"
    POLICY_VIOLATION = "policy_violation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALWARE_ACTIVITY = "malware_activity"
    LATERAL_MOVEMENT = "lateral_movement"

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ESCALATED = "escalated"

# User Management Models
class UserCreate(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    department: str = Field(..., description="User department")
    role: str = Field(..., description="Job role")
    manager_id: Optional[str] = Field(None, description="Manager's user ID")
    start_date: datetime = Field(..., description="Employment start date")
    access_level: str = Field(..., description="Security clearance level")
    location: Optional[str] = Field(None, description="Primary work location")

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    email: str
    department: str
    role: str
    manager_id: Optional[str]
    start_date: datetime
    access_level: str
    location: Optional[str]
    status: str = "active"
    risk_level: str = "low"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Behavioral Data Models
class BehavioralDataPoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User identifier")
    data_type: DataType = Field(..., description="Type of behavioral data")
    timestamp: datetime = Field(..., description="When the data was captured")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    device_id: Optional[str] = Field(None, description="Device identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Keystroke patterns
    typing_speed: Optional[float] = Field(None, description="Characters per minute")
    key_dwell_time: Optional[List[float]] = Field(None, description="Key press durations")
    key_flight_time: Optional[List[float]] = Field(None, description="Time between key presses")
    typing_rhythm: Optional[Dict[str, float]] = Field(None, description="Typing rhythm metrics")
    
    # Mouse patterns
    mouse_velocity: Optional[float] = Field(None, description="Mouse movement velocity")
    click_patterns: Optional[List[Dict]] = Field(None, description="Click timing and patterns")
    scroll_behavior: Optional[Dict] = Field(None, description="Scroll patterns")
    
    # File access patterns
    file_path: Optional[str] = Field(None, description="Accessed file path")
    file_operation: Optional[str] = Field(None, description="File operation type")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    sensitive_data_flag: Optional[bool] = Field(None, description="Contains sensitive data")
    
    # Network patterns
    destination_host: Optional[str] = Field(None, description="Network destination")
    destination_port: Optional[int] = Field(None, description="Destination port")
    protocol: Optional[str] = Field(None, description="Network protocol")
    bytes_sent: Optional[int] = Field(None, description="Bytes sent")
    bytes_received: Optional[int] = Field(None, description="Bytes received")
    
    # Login events
    login_type: Optional[str] = Field(None, description="Login method")
    login_success: Optional[bool] = Field(None, description="Login success status")
    login_location: Optional[str] = Field(None, description="Login location")
    failed_attempts: Optional[int] = Field(None, description="Number of failed attempts")
    
    # Application usage
    application_name: Optional[str] = Field(None, description="Application name")
    window_title: Optional[str] = Field(None, description="Window title")
    usage_duration: Optional[float] = Field(None, description="Usage time in seconds")
    idle_time: Optional[float] = Field(None, description="Idle time in seconds")
    
    # System commands
    command: Optional[str] = Field(None, description="Executed command")
    command_arguments: Optional[List[str]] = Field(None, description="Command arguments")
    execution_success: Optional[bool] = Field(None, description="Command success status")
    elevated_privileges: Optional[bool] = Field(None, description="Used elevated privileges")
    
    # Additional context
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")

class BehavioralDataBatch(BaseModel):
    data: List[BehavioralDataPoint] = Field(..., description="Batch of behavioral data points")
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = Field(..., description="Agent that collected the data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Behavioral Analysis Models
class BehavioralBaseline(BaseModel):
    user_id: str
    data_type: DataType
    baseline_metrics: Dict[str, float] = Field(..., description="Baseline behavioral metrics")
    confidence_score: float = Field(..., description="Confidence in the baseline")
    sample_count: int = Field(..., description="Number of samples used")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AnomalyDetection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    data_point_id: str
    anomaly_type: str = Field(..., description="Type of anomaly detected")
    severity: Severity
    confidence_score: float = Field(..., description="Confidence in anomaly detection")
    deviation_score: float = Field(..., description="How much it deviates from baseline")
    description: str = Field(..., description="Human-readable description")
    details: Dict[str, Any] = Field(..., description="Detailed anomaly information")
    detected_at: datetime = Field(default_factory=datetime.utcnow)

# Threat Detection Models
class ThreatAlert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    threat_type: ThreatType
    severity: Severity
    status: AlertStatus = AlertStatus.OPEN
    score: float = Field(..., description="Threat score (0-100)")
    description: str = Field(..., description="Threat description")
    details: Dict[str, Any] = Field(..., description="Detailed threat information")
    affected_resources: Optional[List[str]] = Field(None, description="Affected resources")
    recommended_actions: Optional[List[str]] = Field(None, description="Recommended actions")
    
    # Investigation fields
    assigned_analyst: Optional[str] = Field(None, description="Assigned analyst ID")
    investigation_notes: Optional[str] = Field(None, description="Investigation notes")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = Field(None)
    resolved_at: Optional[datetime] = Field(None)

class AlertStatusUpdate(BaseModel):
    status: AlertStatus
    notes: Optional[str] = None
    analyst_id: Optional[str] = None

# Risk Scoring Models
class RiskScore(BaseModel):
    user_id: str
    score: float = Field(..., description="Risk score (0-100)")
    risk_level: str = Field(..., description="Risk level (low, medium, high, critical)")
    contributing_factors: List[Dict[str, Any]] = Field(..., description="Factors contributing to risk")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RiskFactor(BaseModel):
    factor_type: str = Field(..., description="Type of risk factor")
    weight: float = Field(..., description="Weight in risk calculation")
    score: float = Field(..., description="Factor score")
    description: str = Field(..., description="Factor description")

# Machine Learning Models
class MLModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Type of ML model")
    version: str = Field(..., description="Model version")
    status: str = Field(default="training", description="Model status")
    accuracy: Optional[float] = Field(None, description="Model accuracy")
    training_data_size: Optional[int] = Field(None, description="Training dataset size")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MLTrainingRequest(BaseModel):
    model_type: str = Field(..., description="Type of model to train")
    user_id: Optional[str] = Field(None, description="Specific user ID for personalized model")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Training parameters")
    data_filter: Optional[Dict[str, Any]] = Field(None, description="Data filtering criteria")

# Detection Rules
class DetectionRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    rule_type: str = Field(..., description="Type of detection rule")
    conditions: Dict[str, Any] = Field(..., description="Rule conditions")
    actions: List[Dict[str, Any]] = Field(..., description="Actions to take when rule triggers")
    severity: Severity = Field(default=Severity.MEDIUM)
    enabled: bool = Field(default=True)
    created_by: str = Field(..., description="Creator of the rule")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Integration Models
class SIEMIntegration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Integration name")
    siem_type: str = Field(..., description="SIEM platform type")
    endpoint: str = Field(..., description="SIEM endpoint URL")
    credentials: Dict[str, str] = Field(..., description="Authentication credentials")
    enabled: bool = Field(default=True)
    last_sync: Optional[datetime] = Field(None)

# Compliance and Audit Models
class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = Field(None, description="User who performed the action")
    action: str = Field(..., description="Action performed")
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: str = Field(..., description="ID of affected resource")
    details: Dict[str, Any] = Field(..., description="Action details")
    ip_address: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ComplianceReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    report_type: str = Field(..., description="Type of compliance report")
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    data: Dict[str, Any] = Field(..., description="Report data")
    generated_by: str = Field(..., description="User who generated the report")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Dashboard Models
class DashboardMetrics(BaseModel):
    total_users: int
    active_threats: int
    alerts_24h: int
    high_risk_users: int
    detection_accuracy: float
    system_health: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class TimeSeriesData(BaseModel):
    timestamp: datetime
    value: float
    label: Optional[str] = None

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]
