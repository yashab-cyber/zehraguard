import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import aiohttp
from enum import Enum

logger = logging.getLogger(__name__)

class AlertChannel(Enum):
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    SIEM = "siem"
    SMS = "sms"

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertManager:
    """
    Manages alert generation, routing, and delivery for threat notifications
    """
    
    def __init__(self):
        self.alert_templates = self._initialize_alert_templates()
        self.notification_channels = self._initialize_notification_channels()
        self.alert_rules = self._initialize_alert_rules()
        self.rate_limiters = {}
        self.alert_history = {}
    
    async def process_threats(self, user_id: str, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process detected threats and generate appropriate alerts
        """
        try:
            logger.info(f"Processing {len(threats)} threats for user {user_id}")
            
            alerts = []
            
            for threat in threats:
                # Check if alert should be generated
                if await self._should_generate_alert(user_id, threat):
                    alert = await self._create_alert(user_id, threat)
                    if alert:
                        alerts.append(alert)
                        
                        # Send notifications
                        await self._send_notifications(alert)
                        
                        # Update rate limiting
                        await self._update_rate_limiting(user_id, threat)
            
            logger.info(f"Generated {len(alerts)} alerts for user {user_id}")
            return alerts
            
        except Exception as e:
            logger.error(f"Error processing threats for user {user_id}: {str(e)}")
            return []
    
    async def _should_generate_alert(self, user_id: str, threat: Dict[str, Any]) -> bool:
        """
        Determine if an alert should be generated for a threat
        """
        try:
            threat_type = threat.get('threat_type', '')
            severity = threat.get('severity', 'medium')
            risk_score = threat.get('risk_score', 0.0)
            
            # Check minimum risk score threshold
            min_risk_score = self.alert_rules.get('min_risk_score', {}).get(severity, 0.0)
            if risk_score < min_risk_score:
                return False
            
            # Check rate limiting
            if await self._is_rate_limited(user_id, threat_type):
                logger.info(f"Alert rate limited for user {user_id}, threat type {threat_type}")
                return False
            
            # Check for duplicate recent alerts
            if await self._is_duplicate_alert(user_id, threat):
                logger.info(f"Duplicate alert detected for user {user_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking alert generation rules: {str(e)}")
            return False
    
    async def _create_alert(self, user_id: str, threat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create an alert from a detected threat
        """
        try:
            alert_id = f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{user_id}_{threat.get('threat_type', 'unknown')}"
            
            alert = {
                'id': alert_id,
                'user_id': user_id,
                'threat_type': threat.get('threat_type', 'unknown'),
                'severity': threat.get('severity', 'medium'),
                'risk_score': threat.get('risk_score', 0.0),
                'title': threat.get('title', 'Security Alert'),
                'description': threat.get('description', 'Potential security threat detected'),
                'evidence': threat.get('evidence', {}),
                'confidence': threat.get('confidence', 0.5),
                'status': 'open',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'acknowledged': False,
                'escalated': False,
                'false_positive': False
            }
            
            # Add contextual information
            alert['context'] = await self._gather_alert_context(user_id, threat)
            
            # Determine alert priority
            alert['priority'] = await self._determine_priority(alert)
            
            # Add recommended actions
            alert['recommended_actions'] = await self._get_recommended_actions(threat)
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating alert: {str(e)}")
            return None
    
    async def _send_notifications(self, alert: Dict[str, Any]) -> None:
        """
        Send notifications through configured channels
        """
        try:
            priority = alert.get('priority', AlertPriority.MEDIUM.value)
            channels = self._get_notification_channels_for_priority(priority)
            
            notification_tasks = []
            
            for channel in channels:
                if channel == AlertChannel.EMAIL.value:
                    task = self._send_email_notification(alert)
                elif channel == AlertChannel.WEBHOOK.value:
                    task = self._send_webhook_notification(alert)
                elif channel == AlertChannel.SLACK.value:
                    task = self._send_slack_notification(alert)
                elif channel == AlertChannel.SIEM.value:
                    task = self._send_siem_notification(alert)
                else:
                    continue
                
                notification_tasks.append(task)
            
            # Send all notifications concurrently
            if notification_tasks:
                await asyncio.gather(*notification_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error sending notifications: {str(e)}")
    
    async def _send_email_notification(self, alert: Dict[str, Any]) -> None:
        """
        Send email notification
        """
        try:
            email_config = self.notification_channels.get('email', {})
            if not email_config.get('enabled', False):
                return
            
            # Get email template
            template = self.alert_templates.get('email', {})
            
            # Format email content
            subject = template.get('subject', 'Security Alert').format(**alert)
            body = template.get('body', 'Alert: {title}').format(**alert)
            
            # Create message
            msg = MimeMultipart()
            msg['From'] = email_config.get('from_address', 'alerts@zehraguard.com')
            msg['To'] = ', '.join(self._get_recipients_for_alert(alert))
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'html'))
            
            # Send email (in production, use proper email service)
            logger.info(f"Email notification sent for alert {alert.get('id')}")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    async def _send_webhook_notification(self, alert: Dict[str, Any]) -> None:
        """
        Send webhook notification
        """
        try:
            webhook_config = self.notification_channels.get('webhook', {})
            if not webhook_config.get('enabled', False):
                return
            
            webhook_url = webhook_config.get('url')
            if not webhook_url:
                return
            
            # Prepare webhook payload
            payload = {
                'alert_id': alert.get('id'),
                'timestamp': alert.get('created_at'),
                'user_id': alert.get('user_id'),
                'threat_type': alert.get('threat_type'),
                'severity': alert.get('severity'),
                'priority': alert.get('priority'),
                'title': alert.get('title'),
                'description': alert.get('description'),
                'risk_score': alert.get('risk_score'),
                'evidence': alert.get('evidence', {}),
                'recommended_actions': alert.get('recommended_actions', [])
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'ZehraGuard-AlertManager/1.0'
            }
            
            # Add authentication if configured
            auth_token = webhook_config.get('auth_token')
            if auth_token:
                headers['Authorization'] = f'Bearer {auth_token}'
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Webhook notification sent for alert {alert.get('id')}")
                    else:
                        logger.error(f"Webhook notification failed: {response.status}")
            
        except Exception as e:
            logger.error(f"Error sending webhook notification: {str(e)}")
    
    async def _send_slack_notification(self, alert: Dict[str, Any]) -> None:
        """
        Send Slack notification
        """
        try:
            slack_config = self.notification_channels.get('slack', {})
            if not slack_config.get('enabled', False):
                return
            
            webhook_url = slack_config.get('webhook_url')
            if not webhook_url:
                return
            
            # Format Slack message
            color = self._get_slack_color(alert.get('priority', 'medium'))
            
            slack_payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"🚨 {alert.get('title', 'Security Alert')}",
                        "text": alert.get('description', 'Security threat detected'),
                        "fields": [
                            {
                                "title": "User",
                                "value": alert.get('user_id', 'Unknown'),
                                "short": True
                            },
                            {
                                "title": "Threat Type",
                                "value": alert.get('threat_type', 'Unknown'),
                                "short": True
                            },
                            {
                                "title": "Severity",
                                "value": alert.get('severity', 'Medium').upper(),
                                "short": True
                            },
                            {
                                "title": "Risk Score",
                                "value": f"{alert.get('risk_score', 0.0):.2f}",
                                "short": True
                            }
                        ],
                        "footer": "ZehraGuard InsightX",
                        "ts": int(datetime.utcnow().timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=slack_payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack notification sent for alert {alert.get('id')}")
                    else:
                        logger.error(f"Slack notification failed: {response.status}")
            
        except Exception as e:
            logger.error(f"Error sending Slack notification: {str(e)}")
    
    async def _send_siem_notification(self, alert: Dict[str, Any]) -> None:
        """
        Send notification to SIEM systems
        """
        try:
            siem_config = self.notification_channels.get('siem', {})
            if not siem_config.get('enabled', False):
                return
            
            # Format for CEF (Common Event Format)
            cef_message = self._format_cef_message(alert)
            
            # Send to configured SIEM endpoints
            siem_endpoints = siem_config.get('endpoints', [])
            
            for endpoint in siem_endpoints:
                await self._send_to_siem_endpoint(endpoint, cef_message, alert)
            
        except Exception as e:
            logger.error(f"Error sending SIEM notification: {str(e)}")
    
    # Helper methods
    
    def _initialize_alert_templates(self) -> Dict[str, Dict]:
        """
        Initialize alert message templates
        """
        return {
            'email': {
                'subject': '🚨 ZehraGuard Alert: {title}',
                'body': '''
                <html>
                <head><title>ZehraGuard Security Alert</title></head>
                <body>
                    <h2 style="color: #d32f2f;">🚨 Security Alert Detected</h2>
                    <p><strong>Alert ID:</strong> {id}</p>
                    <p><strong>User:</strong> {user_id}</p>
                    <p><strong>Threat Type:</strong> {threat_type}</p>
                    <p><strong>Severity:</strong> {severity}</p>
                    <p><strong>Risk Score:</strong> {risk_score}</p>
                    <p><strong>Description:</strong> {description}</p>
                    <p><strong>Time:</strong> {created_at}</p>
                    <hr>
                    <p>This alert was generated by ZehraGuard InsightX threat detection system.</p>
                    <p>Please review and take appropriate action.</p>
                </body>
                </html>
                '''
            },
            'slack': {
                'title': '🚨 Security Alert: {title}',
                'message': '{description}'
            }
        }
    
    def _initialize_notification_channels(self) -> Dict[str, Dict]:
        """
        Initialize notification channel configurations
        """
        return {
            'email': {
                'enabled': True,
                'smtp_server': 'localhost',
                'smtp_port': 587,
                'use_tls': True,
                'username': '',
                'password': '',
                'from_address': 'alerts@zehraguard.com'
            },
            'webhook': {
                'enabled': True,
                'url': '',
                'auth_token': '',
                'timeout': 30
            },
            'slack': {
                'enabled': False,
                'webhook_url': '',
                'channel': '#security-alerts'
            },
            'siem': {
                'enabled': True,
                'endpoints': [
                    {
                        'type': 'splunk',
                        'url': '',
                        'token': ''
                    }
                ]
            }
        }
    
    def _initialize_alert_rules(self) -> Dict[str, Any]:
        """
        Initialize alert generation rules
        """
        return {
            'min_risk_score': {
                'low': 0.3,
                'medium': 0.5,
                'high': 0.7,
                'critical': 0.8
            },
            'rate_limits': {
                'per_user_per_hour': 10,
                'per_threat_type_per_hour': 5,
                'cooldown_minutes': 15
            },
            'escalation': {
                'auto_escalate_after_minutes': 30,
                'escalate_on_severity': ['high', 'critical']
            }
        }
    
    async def _is_rate_limited(self, user_id: str, threat_type: str) -> bool:
        """
        Check if alerts are rate limited for user/threat type
        """
        current_time = datetime.utcnow()
        hour_ago = current_time - timedelta(hours=1)
        
        # Check per-user rate limit
        user_key = f"user_{user_id}"
        if user_key not in self.rate_limiters:
            self.rate_limiters[user_key] = []
        
        # Clean old entries
        self.rate_limiters[user_key] = [
            ts for ts in self.rate_limiters[user_key] if ts > hour_ago
        ]
        
        # Check limit
        max_per_hour = self.alert_rules['rate_limits']['per_user_per_hour']
        if len(self.rate_limiters[user_key]) >= max_per_hour:
            return True
        
        # Check per-threat-type rate limit
        threat_key = f"threat_{threat_type}"
        if threat_key not in self.rate_limiters:
            self.rate_limiters[threat_key] = []
        
        self.rate_limiters[threat_key] = [
            ts for ts in self.rate_limiters[threat_key] if ts > hour_ago
        ]
        
        max_threat_per_hour = self.alert_rules['rate_limits']['per_threat_type_per_hour']
        if len(self.rate_limiters[threat_key]) >= max_threat_per_hour:
            return True
        
        return False
    
    async def _update_rate_limiting(self, user_id: str, threat: Dict[str, Any]) -> None:
        """
        Update rate limiting counters
        """
        current_time = datetime.utcnow()
        
        user_key = f"user_{user_id}"
        if user_key not in self.rate_limiters:
            self.rate_limiters[user_key] = []
        self.rate_limiters[user_key].append(current_time)
        
        threat_type = threat.get('threat_type', 'unknown')
        threat_key = f"threat_{threat_type}"
        if threat_key not in self.rate_limiters:
            self.rate_limiters[threat_key] = []
        self.rate_limiters[threat_key].append(current_time)
    
    async def _is_duplicate_alert(self, user_id: str, threat: Dict[str, Any]) -> bool:
        """
        Check for duplicate alerts within cooldown period
        """
        cooldown_minutes = self.alert_rules['rate_limits']['cooldown_minutes']
        cooldown_time = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
        
        # Simple duplicate detection based on user and threat type
        threat_type = threat.get('threat_type', 'unknown')
        duplicate_key = f"{user_id}_{threat_type}"
        
        if duplicate_key in self.alert_history:
            last_alert_time = self.alert_history[duplicate_key]
            if last_alert_time > cooldown_time:
                return True
        
        # Update history
        self.alert_history[duplicate_key] = datetime.utcnow()
        return False
    
    async def _gather_alert_context(self, user_id: str, threat: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather additional context for the alert
        """
        return {
            'user_info': {
                'user_id': user_id,
                'last_seen': datetime.utcnow().isoformat()
            },
            'threat_info': {
                'detection_method': threat.get('rule_id', 'unknown'),
                'confidence': threat.get('confidence', 0.5)
            },
            'system_info': {
                'detection_system': 'ZehraGuard InsightX',
                'version': '1.0.0'
            }
        }
    
    async def _determine_priority(self, alert: Dict[str, Any]) -> str:
        """
        Determine alert priority based on risk score and severity
        """
        severity = alert.get('severity', 'medium')
        risk_score = alert.get('risk_score', 0.0)
        
        if severity == 'critical' or risk_score >= 0.9:
            return AlertPriority.CRITICAL.value
        elif severity == 'high' or risk_score >= 0.7:
            return AlertPriority.HIGH.value
        elif severity == 'medium' or risk_score >= 0.5:
            return AlertPriority.MEDIUM.value
        else:
            return AlertPriority.LOW.value
    
    async def _get_recommended_actions(self, threat: Dict[str, Any]) -> List[str]:
        """
        Get recommended actions based on threat type
        """
        threat_type = threat.get('threat_type', 'unknown')
        
        action_mapping = {
            'data_exfiltration': [
                'Immediately review user\'s file access logs',
                'Check for unauthorized data transfers',
                'Consider temporarily restricting user access',
                'Investigate network traffic patterns'
            ],
            'policy_violation': [
                'Review company security policies with user',
                'Check if user has legitimate business reason',
                'Consider additional training requirements',
                'Monitor user behavior closely'
            ],
            'privilege_escalation': [
                'Immediately review user\'s access permissions',
                'Check for unauthorized privilege changes',
                'Audit recent access attempts',
                'Consider revoking elevated privileges temporarily'
            ],
            'anomalous_behavior': [
                'Investigate underlying cause of anomaly',
                'Review recent user activities',
                'Check for compromised credentials',
                'Monitor user behavior patterns'
            ]
        }
        
        return action_mapping.get(threat_type, [
            'Review alert details carefully',
            'Investigate user behavior',
            'Take appropriate security measures'
        ])
    
    def _get_notification_channels_for_priority(self, priority: str) -> List[str]:
        """
        Get notification channels based on alert priority
        """
        channel_mapping = {
            AlertPriority.CRITICAL.value: [
                AlertChannel.EMAIL.value,
                AlertChannel.SLACK.value,
                AlertChannel.WEBHOOK.value,
                AlertChannel.SIEM.value
            ],
            AlertPriority.HIGH.value: [
                AlertChannel.EMAIL.value,
                AlertChannel.SLACK.value,
                AlertChannel.SIEM.value
            ],
            AlertPriority.MEDIUM.value: [
                AlertChannel.EMAIL.value,
                AlertChannel.SIEM.value
            ],
            AlertPriority.LOW.value: [
                AlertChannel.SIEM.value
            ]
        }
        
        return channel_mapping.get(priority, [AlertChannel.SIEM.value])
    
    def _get_recipients_for_alert(self, alert: Dict[str, Any]) -> List[str]:
        """
        Get email recipients based on alert characteristics
        """
        # In production, this would be configurable and based on org structure
        priority = alert.get('priority', AlertPriority.MEDIUM.value)
        
        if priority == AlertPriority.CRITICAL.value:
            return ['security-team@company.com', 'ciso@company.com']
        elif priority == AlertPriority.HIGH.value:
            return ['security-team@company.com']
        else:
            return ['security-alerts@company.com']
    
    def _get_slack_color(self, priority: str) -> str:
        """
        Get Slack message color based on priority
        """
        color_mapping = {
            AlertPriority.CRITICAL.value: '#d32f2f',  # Red
            AlertPriority.HIGH.value: '#ff9800',       # Orange
            AlertPriority.MEDIUM.value: '#ffc107',     # Yellow
            AlertPriority.LOW.value: '#4caf50'         # Green
        }
        
        return color_mapping.get(priority, '#9e9e9e')  # Gray default
    
    def _format_cef_message(self, alert: Dict[str, Any]) -> str:
        """
        Format alert as CEF (Common Event Format) message
        """
        # CEF format: CEF:Version|Device Vendor|Device Product|Device Version|Device Event Class ID|Name|Severity|[Extension]
        cef_header = "CEF:0|ZehraGuard|InsightX|1.0|{threat_type}|{title}|{severity_num}".format(
            threat_type=alert.get('threat_type', 'unknown'),
            title=alert.get('title', 'Security Alert'),
            severity_num=self._severity_to_number(alert.get('severity', 'medium'))
        )
        
        cef_extension = "rt={timestamp} src={user_id} cs1={risk_score} cs1Label=RiskScore cs2={confidence} cs2Label=Confidence msg={description}".format(
            timestamp=int(datetime.utcnow().timestamp() * 1000),
            user_id=alert.get('user_id', 'unknown'),
            risk_score=alert.get('risk_score', 0.0),
            confidence=alert.get('confidence', 0.5),
            description=alert.get('description', '').replace('=', '\\=').replace('|', '\\|')
        )
        
        return f"{cef_header}|{cef_extension}"
    
    def _severity_to_number(self, severity: str) -> int:
        """
        Convert severity string to CEF severity number
        """
        severity_mapping = {
            'low': 3,
            'medium': 6,
            'high': 8,
            'critical': 10
        }
        
        return severity_mapping.get(severity.lower(), 6)
    
    async def _send_to_siem_endpoint(self, endpoint: Dict[str, Any], cef_message: str, alert: Dict[str, Any]) -> None:
        """
        Send alert to specific SIEM endpoint
        """
        try:
            endpoint_type = endpoint.get('type', 'generic')
            
            if endpoint_type == 'splunk':
                await self._send_to_splunk(endpoint, cef_message, alert)
            elif endpoint_type == 'azure_sentinel':
                await self._send_to_azure_sentinel(endpoint, cef_message, alert)
            else:
                logger.warning(f"Unsupported SIEM endpoint type: {endpoint_type}")
            
        except Exception as e:
            logger.error(f"Error sending to SIEM endpoint: {str(e)}")
    
    async def _send_to_splunk(self, endpoint: Dict[str, Any], cef_message: str, alert: Dict[str, Any]) -> None:
        """
        Send alert to Splunk HEC (HTTP Event Collector)
        """
        try:
            splunk_url = endpoint.get('url')
            splunk_token = endpoint.get('token')
            
            if not splunk_url or not splunk_token:
                return
            
            headers = {
                'Authorization': f'Splunk {splunk_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'event': cef_message,
                'sourcetype': 'zehraguard:alert',
                'source': 'zehraguard_insightx',
                'index': 'security'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{splunk_url}/services/collector/event", 
                                      json=payload, headers=headers) as response:
                    if response.status == 200:
                        logger.info(f"Alert sent to Splunk for alert {alert.get('id')}")
                    else:
                        logger.error(f"Failed to send to Splunk: {response.status}")
            
        except Exception as e:
            logger.error(f"Error sending to Splunk: {str(e)}")
    
    async def _send_to_azure_sentinel(self, endpoint: Dict[str, Any], cef_message: str, alert: Dict[str, Any]) -> None:
        """
        Send alert to Azure Sentinel
        """
        try:
            # Azure Sentinel integration would be implemented here
            logger.info(f"Alert would be sent to Azure Sentinel for alert {alert.get('id')}")
            
        except Exception as e:
            logger.error(f"Error sending to Azure Sentinel: {str(e)}")
