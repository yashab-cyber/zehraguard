import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class ThreatType(Enum):
    DATA_EXFILTRATION = "data_exfiltration"
    INSIDER_TRADING = "insider_trading"
    POLICY_VIOLATION = "policy_violation"
    ANOMALOUS_BEHAVIOR = "anomalous_behavior"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    MALWARE_ACTIVITY = "malware_activity"
    LATERAL_MOVEMENT = "lateral_movement"

class ThreatDetector:
    """
    Advanced threat detection engine that analyzes behavioral patterns
    and identifies potential insider threats
    """
    
    def __init__(self):
        self.detection_rules = self._initialize_detection_rules()
        self.threat_patterns = self._initialize_threat_patterns()
        self.risk_models = self._initialize_risk_models()
        self.baseline_cache = {}
    
    async def detect_threats(self, user_id: str, behavioral_analysis: Dict[str, Any], 
                           events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Main threat detection method
        """
        try:
            logger.info(f"Running threat detection for user {user_id}")
            
            threats = []
            
            # Rule-based detection
            rule_threats = await self._rule_based_detection(user_id, behavioral_analysis, events)
            threats.extend(rule_threats)
            
            # Pattern-based detection
            pattern_threats = await self._pattern_based_detection(user_id, behavioral_analysis, events)
            threats.extend(pattern_threats)
            
            # Anomaly-based detection
            anomaly_threats = await self._anomaly_based_detection(user_id, behavioral_analysis, events)
            threats.extend(anomaly_threats)
            
            # ML-based detection
            ml_threats = await self._ml_based_detection(user_id, behavioral_analysis, events)
            threats.extend(ml_threats)
            
            # Correlate and deduplicate threats
            correlated_threats = await self._correlate_threats(threats)
            
            # Calculate final risk scores
            final_threats = await self._calculate_risk_scores(correlated_threats)
            
            logger.info(f"Detected {len(final_threats)} threats for user {user_id}")
            return final_threats
            
        except Exception as e:
            logger.error(f"Error in threat detection for user {user_id}: {str(e)}")
            return []
    
    def _initialize_detection_rules(self) -> Dict[str, Dict]:
        """
        Initialize threat detection rules
        """
        return {
            "data_exfiltration": {
                "large_file_access": {
                    "threshold": 100000000,  # 100MB
                    "severity": "high",
                    "description": "Large file access detected"
                },
                "unusual_file_types": {
                    "suspicious_extensions": [".db", ".sql", ".csv", ".xlsx", ".pst"],
                    "severity": "medium",
                    "description": "Access to sensitive file types"
                },
                "bulk_download": {
                    "threshold": 50,  # files per hour
                    "severity": "high",
                    "description": "Bulk file download detected"
                }
            },
            "policy_violation": {
                "after_hours_access": {
                    "work_hours_ratio_threshold": 0.3,
                    "severity": "medium",
                    "description": "Excessive after-hours activity"
                },
                "unauthorized_location": {
                    "max_locations": 3,
                    "severity": "high",
                    "description": "Access from unauthorized locations"
                }
            },
            "privilege_escalation": {
                "admin_access_attempt": {
                    "failed_admin_threshold": 5,
                    "severity": "critical",
                    "description": "Multiple failed admin access attempts"
                },
                "new_privilege_usage": {
                    "severity": "medium",
                    "description": "Usage of newly granted privileges"
                }
            }
        }
    
    def _initialize_threat_patterns(self) -> Dict[str, Dict]:
        """
        Initialize threat behavior patterns
        """
        return {
            "data_exfiltration_pattern": {
                "sequence": ["large_file_access", "external_transfer", "deletion"],
                "timeframe": 3600,  # 1 hour
                "severity": "critical"
            },
            "insider_trading_pattern": {
                "sequence": ["financial_data_access", "trading_platform_usage", "unusual_timing"],
                "timeframe": 7200,  # 2 hours
                "severity": "critical"
            },
            "reconnaissance_pattern": {
                "sequence": ["directory_enumeration", "privilege_check", "network_scan"],
                "timeframe": 1800,  # 30 minutes
                "severity": "high"
            }
        }
    
    def _initialize_risk_models(self) -> Dict[str, Dict]:
        """
        Initialize risk scoring models
        """
        return {
            "user_risk_factors": {
                "access_level": {"admin": 0.8, "manager": 0.6, "employee": 0.3},
                "department": {"finance": 0.7, "hr": 0.6, "it": 0.8, "sales": 0.4},
                "tenure": {"<6months": 0.7, "6-24months": 0.4, ">24months": 0.2}
            },
            "behavioral_weights": {
                "anomaly_score": 0.4,
                "policy_violations": 0.3,
                "data_access_patterns": 0.2,
                "login_anomalies": 0.1
            }
        }
    
    async def _rule_based_detection(self, user_id: str, behavioral_analysis: Dict[str, Any], 
                                  events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rule-based threat detection
        """
        threats = []
        
        try:
            # Data exfiltration rules
            data_threats = await self._check_data_exfiltration_rules(behavioral_analysis, events)
            threats.extend(data_threats)
            
            # Policy violation rules
            policy_threats = await self._check_policy_violation_rules(behavioral_analysis, events)
            threats.extend(policy_threats)
            
            # Privilege escalation rules
            privilege_threats = await self._check_privilege_escalation_rules(behavioral_analysis, events)
            threats.extend(privilege_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in rule-based detection: {str(e)}")
            return []
    
    async def _check_data_exfiltration_rules(self, behavioral_analysis: Dict[str, Any], 
                                           events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for data exfiltration indicators
        """
        threats = []
        
        # Large file access
        total_data_volume = behavioral_analysis.get('total_data_volume', 0)
        if total_data_volume > self.detection_rules["data_exfiltration"]["large_file_access"]["threshold"]:
            threats.append({
                "threat_type": ThreatType.DATA_EXFILTRATION.value,
                "rule_id": "large_file_access",
                "severity": "high",
                "title": "Large Data Volume Access",
                "description": f"User accessed {total_data_volume / 1000000:.1f}MB of data",
                "evidence": {"total_data_volume": total_data_volume},
                "confidence": 0.8
            })
        
        # Bulk download detection
        file_access_count = behavioral_analysis.get('total_file_accesses', 0)
        if file_access_count > self.detection_rules["data_exfiltration"]["bulk_download"]["threshold"]:
            threats.append({
                "threat_type": ThreatType.DATA_EXFILTRATION.value,
                "rule_id": "bulk_download",
                "severity": "high",
                "title": "Bulk File Download",
                "description": f"User accessed {file_access_count} files in short timeframe",
                "evidence": {"file_access_count": file_access_count},
                "confidence": 0.7
            })
        
        # Suspicious file types
        suspicious_files = await self._check_suspicious_file_access(events)
        if suspicious_files:
            threats.append({
                "threat_type": ThreatType.DATA_EXFILTRATION.value,
                "rule_id": "suspicious_file_types",
                "severity": "medium",
                "title": "Suspicious File Type Access",
                "description": f"User accessed {len(suspicious_files)} sensitive files",
                "evidence": {"suspicious_files": suspicious_files},
                "confidence": 0.6
            })
        
        return threats
    
    async def _check_policy_violation_rules(self, behavioral_analysis: Dict[str, Any], 
                                          events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for policy violations
        """
        threats = []
        
        # After-hours access
        work_hours_ratio = behavioral_analysis.get('work_hours_ratio', 1.0)
        if work_hours_ratio < self.detection_rules["policy_violation"]["after_hours_access"]["work_hours_ratio_threshold"]:
            threats.append({
                "threat_type": ThreatType.POLICY_VIOLATION.value,
                "rule_id": "after_hours_access",
                "severity": "medium",
                "title": "Excessive After-Hours Activity",
                "description": f"Only {work_hours_ratio*100:.1f}% of activity during work hours",
                "evidence": {"work_hours_ratio": work_hours_ratio},
                "confidence": 0.7
            })
        
        # Multiple location access
        unique_locations = behavioral_analysis.get('unique_login_locations', 0)
        if unique_locations > self.detection_rules["policy_violation"]["unauthorized_location"]["max_locations"]:
            threats.append({
                "threat_type": ThreatType.POLICY_VIOLATION.value,
                "rule_id": "multiple_locations",
                "severity": "high",
                "title": "Multiple Location Access",
                "description": f"User accessed from {unique_locations} different locations",
                "evidence": {"unique_locations": unique_locations},
                "confidence": 0.8
            })
        
        return threats
    
    async def _check_privilege_escalation_rules(self, behavioral_analysis: Dict[str, Any], 
                                              events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for privilege escalation attempts
        """
        threats = []
        
        # Failed login attempts
        failed_attempts = behavioral_analysis.get('failed_login_attempts', 0)
        if failed_attempts > 3:
            threats.append({
                "threat_type": ThreatType.PRIVILEGE_ESCALATION.value,
                "rule_id": "failed_login_attempts",
                "severity": "medium",
                "title": "Multiple Failed Login Attempts",
                "description": f"User had {failed_attempts} failed login attempts",
                "evidence": {"failed_attempts": failed_attempts},
                "confidence": 0.6
            })
        
        return threats
    
    async def _pattern_based_detection(self, user_id: str, behavioral_analysis: Dict[str, Any], 
                                     events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pattern-based threat detection
        """
        threats = []
        
        try:
            # Check for each threat pattern
            for pattern_name, pattern_config in self.threat_patterns.items():
                pattern_threats = await self._check_threat_pattern(
                    pattern_name, pattern_config, events
                )
                threats.extend(pattern_threats)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in pattern-based detection: {str(e)}")
            return []
    
    async def _check_threat_pattern(self, pattern_name: str, pattern_config: Dict, 
                                  events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Check for specific threat patterns in event sequence
        """
        threats = []
        
        # Simple pattern matching - in production, this would be more sophisticated
        sequence = pattern_config["sequence"]
        timeframe = pattern_config["timeframe"]
        
        # Group events by time windows
        time_windows = self._group_events_by_time(events, timeframe)
        
        for window_events in time_windows:
            if await self._matches_pattern(window_events, sequence):
                threats.append({
                    "threat_type": self._pattern_to_threat_type(pattern_name),
                    "rule_id": pattern_name,
                    "severity": pattern_config["severity"],
                    "title": f"Threat Pattern Detected: {pattern_name}",
                    "description": f"Event sequence matches {pattern_name} pattern",
                    "evidence": {"pattern": sequence, "events": len(window_events)},
                    "confidence": 0.9
                })
        
        return threats
    
    async def _anomaly_based_detection(self, user_id: str, behavioral_analysis: Dict[str, Any], 
                                     events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Anomaly-based threat detection
        """
        threats = []
        
        try:
            anomaly_score = behavioral_analysis.get('anomaly_score', 0.0)
            
            if anomaly_score > 0.8:
                threats.append({
                    "threat_type": ThreatType.ANOMALOUS_BEHAVIOR.value,
                    "rule_id": "high_anomaly_score",
                    "severity": "high",
                    "title": "High Behavioral Anomaly",
                    "description": f"User behavior anomaly score: {anomaly_score:.2f}",
                    "evidence": {"anomaly_score": anomaly_score},
                    "confidence": anomaly_score
                })
            
            # Check specific anomalies
            anomalies = behavioral_analysis.get('anomalies', [])
            for anomaly in anomalies:
                threats.append({
                    "threat_type": ThreatType.ANOMALOUS_BEHAVIOR.value,
                    "rule_id": f"anomaly_{anomaly['type']}",
                    "severity": anomaly.get('severity', 'medium'),
                    "title": f"Behavioral Anomaly: {anomaly['type']}",
                    "description": anomaly.get('description', 'Behavioral anomaly detected'),
                    "evidence": anomaly,
                    "confidence": 0.7
                })
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in anomaly-based detection: {str(e)}")
            return []
    
    async def _ml_based_detection(self, user_id: str, behavioral_analysis: Dict[str, Any], 
                                events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Machine learning-based threat detection
        """
        threats = []
        
        try:
            # This would integrate with the ML service for advanced detection
            # For now, we'll use simple heuristics based on behavioral analysis
            
            risk_score = await self._calculate_ml_risk_score(behavioral_analysis)
            
            if risk_score > 0.75:
                threats.append({
                    "threat_type": ThreatType.ANOMALOUS_BEHAVIOR.value,
                    "rule_id": "ml_high_risk",
                    "severity": "high",
                    "title": "ML Model High Risk Score",
                    "description": f"ML model calculated high risk score: {risk_score:.2f}",
                    "evidence": {"ml_risk_score": risk_score},
                    "confidence": risk_score
                })
            
            return threats
            
        except Exception as e:
            logger.error(f"Error in ML-based detection: {str(e)}")
            return []
    
    async def _correlate_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Correlate and deduplicate similar threats
        """
        if not threats:
            return []
        
        # Simple correlation - group by threat type and merge similar ones
        threat_groups = {}
        for threat in threats:
            threat_type = threat.get('threat_type', 'unknown')
            if threat_type not in threat_groups:
                threat_groups[threat_type] = []
            threat_groups[threat_type].append(threat)
        
        correlated_threats = []
        for threat_type, group_threats in threat_groups.items():
            if len(group_threats) == 1:
                correlated_threats.append(group_threats[0])
            else:
                # Merge multiple threats of same type
                merged_threat = await self._merge_threats(group_threats)
                correlated_threats.append(merged_threat)
        
        return correlated_threats
    
    async def _calculate_risk_scores(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate final risk scores for threats
        """
        for threat in threats:
            base_confidence = threat.get('confidence', 0.5)
            severity = threat.get('severity', 'medium')
            
            # Severity multiplier
            severity_multiplier = {
                'low': 0.3,
                'medium': 0.6,
                'high': 0.8,
                'critical': 1.0
            }.get(severity, 0.6)
            
            # Calculate final risk score
            risk_score = base_confidence * severity_multiplier
            threat['risk_score'] = min(1.0, risk_score)
            threat['timestamp'] = datetime.utcnow().isoformat()
        
        return threats
    
    # Helper methods
    
    async def _check_suspicious_file_access(self, events: List[Dict[str, Any]]) -> List[str]:
        """
        Check for access to suspicious file types
        """
        suspicious_files = []
        suspicious_extensions = self.detection_rules["data_exfiltration"]["unusual_file_types"]["suspicious_extensions"]
        
        for event in events:
            if event.get('event_type') == 'file_access':
                file_path = event.get('event_data', {}).get('file_path', '')
                for ext in suspicious_extensions:
                    if file_path.endswith(ext):
                        suspicious_files.append(file_path)
                        break
        
        return suspicious_files
    
    def _group_events_by_time(self, events: List[Dict[str, Any]], timeframe: int) -> List[List[Dict]]:
        """
        Group events into time windows
        """
        if not events:
            return []
        
        # Sort events by timestamp
        sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
        
        windows = []
        current_window = []
        window_start = None
        
        for event in sorted_events:
            event_time = datetime.fromisoformat(event.get('timestamp', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            
            if window_start is None:
                window_start = event_time
                current_window = [event]
            elif (event_time - window_start).total_seconds() <= timeframe:
                current_window.append(event)
            else:
                if current_window:
                    windows.append(current_window)
                window_start = event_time
                current_window = [event]
        
        if current_window:
            windows.append(current_window)
        
        return windows
    
    async def _matches_pattern(self, events: List[Dict[str, Any]], sequence: List[str]) -> bool:
        """
        Check if events match a specific pattern sequence
        """
        # Simple pattern matching - check if all sequence elements are present
        event_types = [event.get('event_type', '') for event in events]
        
        for seq_item in sequence:
            if seq_item not in event_types:
                return False
        
        return True
    
    def _pattern_to_threat_type(self, pattern_name: str) -> str:
        """
        Map pattern name to threat type
        """
        pattern_mapping = {
            "data_exfiltration_pattern": ThreatType.DATA_EXFILTRATION.value,
            "insider_trading_pattern": ThreatType.INSIDER_TRADING.value,
            "reconnaissance_pattern": ThreatType.PRIVILEGE_ESCALATION.value
        }
        
        return pattern_mapping.get(pattern_name, ThreatType.ANOMALOUS_BEHAVIOR.value)
    
    async def _calculate_ml_risk_score(self, behavioral_analysis: Dict[str, Any]) -> float:
        """
        Calculate ML-based risk score
        """
        # Simple weighted scoring based on behavioral features
        weights = self.risk_models["behavioral_weights"]
        
        anomaly_score = behavioral_analysis.get('anomaly_score', 0.0)
        work_hours_ratio = behavioral_analysis.get('work_hours_ratio', 1.0)
        failed_login_rate = 1 - behavioral_analysis.get('login_success_rate', 1.0)
        data_volume = min(1.0, behavioral_analysis.get('total_data_volume', 0) / 100000000)  # Normalize to 100MB
        
        risk_score = (
            anomaly_score * weights["anomaly_score"] +
            (1 - work_hours_ratio) * weights["policy_violations"] +
            data_volume * weights["data_access_patterns"] +
            failed_login_rate * weights["login_anomalies"]
        )
        
        return min(1.0, risk_score)
    
    async def _merge_threats(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge multiple similar threats into one
        """
        if not threats:
            return {}
        
        # Take the highest severity threat as base
        base_threat = max(threats, key=lambda x: {
            'low': 1, 'medium': 2, 'high': 3, 'critical': 4
        }.get(x.get('severity', 'medium'), 2))
        
        # Combine evidence
        combined_evidence = {}
        for threat in threats:
            evidence = threat.get('evidence', {})
            combined_evidence.update(evidence)
        
        # Calculate average confidence
        confidences = [t.get('confidence', 0.5) for t in threats]
        avg_confidence = sum(confidences) / len(confidences)
        
        merged_threat = base_threat.copy()
        merged_threat['evidence'] = combined_evidence
        merged_threat['confidence'] = avg_confidence
        merged_threat['description'] = f"Multiple indicators detected: {', '.join([t.get('title', '') for t in threats])}"
        merged_threat['rule_id'] = f"merged_{base_threat.get('threat_type', 'unknown')}"
        
        return merged_threat
