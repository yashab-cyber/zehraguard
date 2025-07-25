from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from .database import get_db, Database
from .models import *
from .services.behavioral_analyzer import BehavioralAnalyzer
from .services.threat_detector import ThreatDetector
from .services.alert_manager import AlertManager
from .services.ml_service import MLService
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ZehraGuard InsightX API",
    description="AI-powered insider threat detection system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Services
behavioral_analyzer = BehavioralAnalyzer()
threat_detector = ThreatDetector()
alert_manager = AlertManager()
ml_service = MLService()

# WebSocket connections for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {
        "message": "ZehraGuard InsightX API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "ml_service": "operational",
            "behavioral_analyzer": "running",
            "threat_detector": "active"
        }
    }

# User Management Endpoints
@app.post("/api/v1/users", response_model=UserProfile)
async def create_user(user: UserCreate, db: Database = Depends(get_db)):
    """Create a new user profile for monitoring"""
    try:
        # Create user profile
        user_profile = await db.create_user_profile(user)
        
        # Initialize behavioral baseline
        await behavioral_analyzer.initialize_baseline(user_profile.id)
        
        return user_profile
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: str, db: Database = Depends(get_db)):
    """Get user profile by ID"""
    user = await db.get_user_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/v1/users", response_model=List[UserProfile])
async def list_users(skip: int = 0, limit: int = 100, db: Database = Depends(get_db)):
    """List all user profiles"""
    return await db.list_user_profiles(skip=skip, limit=limit)

# Behavioral Data Endpoints
@app.post("/api/v1/behavioral-data")
async def ingest_behavioral_data(data: BehavioralDataBatch, db: Database = Depends(get_db)):
    """Ingest behavioral data from agents"""
    try:
        # Store behavioral data
        await db.store_behavioral_data(data.data)
        
        # Process each data point for anomalies
        for data_point in data.data:
            # Analyze behavior
            analysis = await behavioral_analyzer.analyze_behavior(data_point)
            
            # Detect threats
            threat_score = await threat_detector.calculate_threat_score(data_point, analysis)
            
            # Check if threat score exceeds threshold
            if threat_score > settings.THREAT_THRESHOLD:
                alert = ThreatAlert(
                    user_id=data_point.user_id,
                    threat_type=analysis.anomaly_type,
                    severity=analysis.severity,
                    score=threat_score,
                    description=analysis.description,
                    details=analysis.details,
                    timestamp=datetime.utcnow()
                )
                
                # Create alert
                await alert_manager.create_alert(alert)
                
                # Broadcast alert to connected clients
                await manager.broadcast(json.dumps({
                    "type": "threat_alert",
                    "data": alert.dict()
                }))
        
        return {"status": "success", "processed": len(data.data)}
        
    except Exception as e:
        logger.error(f"Error processing behavioral data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/behavioral-data/{user_id}")
async def get_user_behavioral_data(
    user_id: str,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    data_type: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Get behavioral data for a specific user"""
    if not start_time:
        start_time = datetime.utcnow() - timedelta(days=7)
    if not end_time:
        end_time = datetime.utcnow()
    
    data = await db.get_behavioral_data(
        user_id=user_id,
        start_time=start_time,
        end_time=end_time,
        data_type=data_type
    )
    
    return {"data": data, "count": len(data)}

# Threat Detection Endpoints
@app.get("/api/v1/threats/alerts", response_model=List[ThreatAlert])
async def get_threat_alerts(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Database = Depends(get_db)
):
    """Get threat alerts with optional filtering"""
    return await db.get_threat_alerts(
        skip=skip,
        limit=limit,
        severity=severity,
        status=status
    )

@app.get("/api/v1/threats/alerts/{alert_id}", response_model=ThreatAlert)
async def get_threat_alert(alert_id: str, db: Database = Depends(get_db)):
    """Get specific threat alert by ID"""
    alert = await db.get_threat_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@app.put("/api/v1/threats/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: str,
    status_update: AlertStatusUpdate,
    db: Database = Depends(get_db)
):
    """Update the status of a threat alert"""
    success = await db.update_alert_status(alert_id, status_update.status, status_update.notes)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"status": "updated", "alert_id": alert_id}

@app.get("/api/v1/threats/dashboard")
async def get_threat_dashboard(db: Database = Depends(get_db)):
    """Get dashboard data for threat overview"""
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    dashboard_data = {
        "summary": {
            "total_alerts_24h": await db.count_alerts(start_time=last_24h),
            "total_alerts_7d": await db.count_alerts(start_time=last_7d),
            "high_risk_users": await db.count_high_risk_users(),
            "active_threats": await db.count_active_threats()
        },
        "alerts_by_severity": await db.get_alerts_by_severity(start_time=last_7d),
        "top_threat_types": await db.get_top_threat_types(start_time=last_7d),
        "user_risk_distribution": await db.get_user_risk_distribution(),
        "recent_alerts": await db.get_threat_alerts(limit=10)
    }
    
    return dashboard_data

# Machine Learning Endpoints
@app.post("/api/v1/ml/train")
async def train_model(training_request: MLTrainingRequest):
    """Trigger ML model training"""
    try:
        job_id = await ml_service.start_training(
            model_type=training_request.model_type,
            user_id=training_request.user_id,
            parameters=training_request.parameters
        )
        
        return {"job_id": job_id, "status": "training_started"}
    
    except Exception as e:
        logger.error(f"Error starting ML training: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ml/models")
async def list_models():
    """List available ML models"""
    models = await ml_service.list_models()
    return {"models": models}

@app.get("/api/v1/ml/models/{model_id}/performance")
async def get_model_performance(model_id: str):
    """Get model performance metrics"""
    performance = await ml_service.get_model_performance(model_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Model not found")
    return performance

# User Risk Scoring
@app.get("/api/v1/users/{user_id}/risk-score")
async def get_user_risk_score(user_id: str, db: Database = Depends(get_db)):
    """Get current risk score for a user"""
    risk_score = await threat_detector.get_current_risk_score(user_id)
    risk_history = await db.get_risk_score_history(user_id, limit=30)
    
    return {
        "user_id": user_id,
        "current_risk_score": risk_score,
        "risk_level": threat_detector.get_risk_level(risk_score),
        "history": risk_history,
        "last_updated": datetime.utcnow()
    }

@app.get("/api/v1/users/{user_id}/behavioral-profile")
async def get_user_behavioral_profile(user_id: str, db: Database = Depends(get_db)):
    """Get behavioral profile for a user"""
    profile = await behavioral_analyzer.get_behavioral_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Behavioral profile not found")
    
    return profile

# Investigation Tools
@app.get("/api/v1/investigation/{user_id}/timeline")
async def get_user_activity_timeline(
    user_id: str,
    start_time: datetime,
    end_time: datetime,
    db: Database = Depends(get_db)
):
    """Get detailed activity timeline for investigation"""
    timeline = await db.get_user_activity_timeline(user_id, start_time, end_time)
    
    return {
        "user_id": user_id,
        "timeline": timeline,
        "period": {
            "start": start_time,
            "end": end_time
        }
    }

@app.get("/api/v1/investigation/{user_id}/anomalies")
async def get_user_anomalies(
    user_id: str,
    days: int = 30,
    db: Database = Depends(get_db)
):
    """Get detected anomalies for a user"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    anomalies = await db.get_user_anomalies(user_id, start_time, end_time)
    
    return {
        "user_id": user_id,
        "anomalies": anomalies,
        "period_days": days
    }

# Configuration and Settings
@app.get("/api/v1/config/detection-rules")
async def get_detection_rules(db: Database = Depends(get_db)):
    """Get current detection rules"""
    return await db.get_detection_rules()

@app.post("/api/v1/config/detection-rules")
async def create_detection_rule(rule: DetectionRule, db: Database = Depends(get_db)):
    """Create new detection rule"""
    rule_id = await db.create_detection_rule(rule)
    return {"rule_id": rule_id, "status": "created"}

@app.put("/api/v1/config/detection-rules/{rule_id}")
async def update_detection_rule(rule_id: str, rule: DetectionRule, db: Database = Depends(get_db)):
    """Update detection rule"""
    success = await db.update_detection_rule(rule_id, rule)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return {"rule_id": rule_id, "status": "updated"}

# Export and Reporting
@app.get("/api/v1/reports/compliance")
async def generate_compliance_report(
    start_date: datetime,
    end_date: datetime,
    compliance_type: str,
    db: Database = Depends(get_db)
):
    """Generate compliance report"""
    report = await db.generate_compliance_report(start_date, end_date, compliance_type)
    
    return {
        "report_type": compliance_type,
        "period": {"start": start_date, "end": end_date},
        "data": report,
        "generated_at": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
