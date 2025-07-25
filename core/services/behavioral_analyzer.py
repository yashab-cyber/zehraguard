import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import json

logger = logging.getLogger(__name__)

class BehavioralAnalyzer:
    """
    Analyzes user behavioral patterns and detects anomalies
    """
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.baseline_models = {}
        self.feature_extractors = {
            'keystroke': self._extract_keystroke_features,
            'mouse_movement': self._extract_mouse_features,
            'file_access': self._extract_file_features,
            'network_request': self._extract_network_features,
            'login_event': self._extract_login_features,
            'application_usage': self._extract_app_features
        }
    
    async def analyze_user_behavior(self, user_id: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze behavioral patterns for a specific user
        """
        try:
            logger.info(f"Analyzing behavior for user {user_id} with {len(events)} events")
            
            # Extract features from events
            features = await self._extract_behavioral_features(events)
            
            if not features:
                return {
                    'user_id': user_id,
                    'anomaly_score': 0.0,
                    'risk_level': 'low',
                    'patterns': {},
                    'anomalies': []
                }
            
            # Calculate anomaly scores
            anomaly_score = await self._calculate_anomaly_score(user_id, features)
            
            # Detect specific behavioral patterns
            patterns = await self._detect_patterns(features)
            
            # Identify anomalies
            anomalies = await self._identify_anomalies(features, anomaly_score)
            
            # Determine risk level
            risk_level = self._determine_risk_level(anomaly_score)
            
            return {
                'user_id': user_id,
                'anomaly_score': float(anomaly_score),
                'risk_level': risk_level,
                'patterns': patterns,
                'anomalies': anomalies,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'event_count': len(events)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing behavior for user {user_id}: {str(e)}")
            raise
    
    async def _extract_behavioral_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract behavioral features from user events
        """
        features = {}
        
        # Group events by type
        events_by_type = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            if event_type not in events_by_type:
                events_by_type[event_type] = []
            events_by_type[event_type].append(event)
        
        # Extract features for each event type
        for event_type, type_events in events_by_type.items():
            if event_type in self.feature_extractors:
                type_features = await self.feature_extractors[event_type](type_events)
                features.update(type_features)
        
        # Calculate temporal features
        temporal_features = await self._extract_temporal_features(events)
        features.update(temporal_features)
        
        return features
    
    async def _extract_keystroke_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract keystroke dynamics features
        """
        if not events:
            return {}
        
        dwell_times = []
        flight_times = []
        typing_speeds = []
        
        for event in events:
            data = event.get('event_data', {})
            if 'dwell_time' in data:
                dwell_times.append(data['dwell_time'])
            if 'flight_time' in data:
                flight_times.append(data['flight_time'])
            if 'typing_speed' in data:
                typing_speeds.append(data['typing_speed'])
        
        features = {}
        if dwell_times:
            features.update({
                'avg_dwell_time': np.mean(dwell_times),
                'std_dwell_time': np.std(dwell_times),
                'median_dwell_time': np.median(dwell_times)
            })
        
        if flight_times:
            features.update({
                'avg_flight_time': np.mean(flight_times),
                'std_flight_time': np.std(flight_times),
                'median_flight_time': np.median(flight_times)
            })
        
        if typing_speeds:
            features.update({
                'avg_typing_speed': np.mean(typing_speeds),
                'std_typing_speed': np.std(typing_speeds),
                'max_typing_speed': np.max(typing_speeds)
            })
        
        return features
    
    async def _extract_mouse_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract mouse movement features
        """
        if not events:
            return {}
        
        velocities = []
        accelerations = []
        click_frequencies = []
        
        for event in events:
            data = event.get('event_data', {})
            if 'velocity' in data:
                velocities.append(data['velocity'])
            if 'acceleration' in data:
                accelerations.append(data['acceleration'])
            if 'click_frequency' in data:
                click_frequencies.append(data['click_frequency'])
        
        features = {}
        if velocities:
            features.update({
                'avg_mouse_velocity': np.mean(velocities),
                'std_mouse_velocity': np.std(velocities),
                'max_mouse_velocity': np.max(velocities)
            })
        
        if accelerations:
            features.update({
                'avg_mouse_acceleration': np.mean(accelerations),
                'std_mouse_acceleration': np.std(accelerations)
            })
        
        if click_frequencies:
            features.update({
                'avg_click_frequency': np.mean(click_frequencies),
                'total_clicks': len(click_frequencies)
            })
        
        return features
    
    async def _extract_file_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract file access pattern features
        """
        if not events:
            return {}
        
        file_types = set()
        access_times = []
        file_sizes = []
        unique_files = set()
        
        for event in events:
            data = event.get('event_data', {})
            if 'file_type' in data:
                file_types.add(data['file_type'])
            if 'access_time' in data:
                access_times.append(data['access_time'])
            if 'file_size' in data:
                file_sizes.append(data['file_size'])
            if 'file_path' in data:
                unique_files.add(data['file_path'])
        
        features = {
            'unique_file_types': len(file_types),
            'total_file_accesses': len(events),
            'unique_files_accessed': len(unique_files)
        }
        
        if file_sizes:
            features.update({
                'avg_file_size': np.mean(file_sizes),
                'total_file_size': np.sum(file_sizes),
                'max_file_size': np.max(file_sizes)
            })
        
        return features
    
    async def _extract_network_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract network request features
        """
        if not events:
            return {}
        
        domains = set()
        protocols = set()
        data_volumes = []
        request_frequencies = []
        
        for event in events:
            data = event.get('event_data', {})
            if 'domain' in data:
                domains.add(data['domain'])
            if 'protocol' in data:
                protocols.add(data['protocol'])
            if 'data_volume' in data:
                data_volumes.append(data['data_volume'])
        
        features = {
            'unique_domains': len(domains),
            'unique_protocols': len(protocols),
            'total_network_requests': len(events)
        }
        
        if data_volumes:
            features.update({
                'total_data_volume': np.sum(data_volumes),
                'avg_data_volume': np.mean(data_volumes),
                'max_data_volume': np.max(data_volumes)
            })
        
        return features
    
    async def _extract_login_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract login pattern features
        """
        if not events:
            return {}
        
        locations = set()
        devices = set()
        login_times = []
        failed_attempts = 0
        
        for event in events:
            data = event.get('event_data', {})
            if 'location' in data:
                locations.add(data['location'])
            if 'device_id' in data:
                devices.add(data['device_id'])
            if 'login_time' in data:
                login_times.append(data['login_time'])
            if data.get('success', True) == False:
                failed_attempts += 1
        
        features = {
            'unique_login_locations': len(locations),
            'unique_devices': len(devices),
            'total_login_attempts': len(events),
            'failed_login_attempts': failed_attempts,
            'login_success_rate': (len(events) - failed_attempts) / len(events) if events else 0
        }
        
        return features
    
    async def _extract_app_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract application usage features
        """
        if not events:
            return {}
        
        applications = set()
        usage_durations = []
        
        for event in events:
            data = event.get('event_data', {})
            if 'application' in data:
                applications.add(data['application'])
            if 'duration' in data:
                usage_durations.append(data['duration'])
        
        features = {
            'unique_applications': len(applications),
            'total_app_sessions': len(events)
        }
        
        if usage_durations:
            features.update({
                'total_usage_time': np.sum(usage_durations),
                'avg_session_duration': np.mean(usage_durations),
                'max_session_duration': np.max(usage_durations)
            })
        
        return features
    
    async def _extract_temporal_features(self, events: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Extract temporal pattern features
        """
        if not events:
            return {}
        
        timestamps = [datetime.fromisoformat(event.get('timestamp', datetime.utcnow().isoformat()).replace('Z', '+00:00')) for event in events]
        timestamps.sort()
        
        # Work hours analysis (9 AM to 5 PM)
        work_hours_events = 0
        for ts in timestamps:
            if 9 <= ts.hour <= 17:
                work_hours_events += 1
        
        # Calculate time intervals between events
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        features = {
            'events_in_work_hours': work_hours_events,
            'work_hours_ratio': work_hours_events / len(events) if events else 0,
            'total_time_span': (timestamps[-1] - timestamps[0]).total_seconds() if len(timestamps) > 1 else 0
        }
        
        if intervals:
            features.update({
                'avg_event_interval': np.mean(intervals),
                'std_event_interval': np.std(intervals),
                'median_event_interval': np.median(intervals)
            })
        
        return features
    
    async def _calculate_anomaly_score(self, user_id: str, features: Dict[str, float]) -> float:
        """
        Calculate anomaly score for user features
        """
        if not features:
            return 0.0
        
        # Convert features to array
        feature_array = np.array(list(features.values())).reshape(1, -1)
        
        # Use isolation forest for anomaly detection
        try:
            # If we have a baseline model for this user, use it
            if user_id in self.baseline_models:
                score = self.baseline_models[user_id].decision_function(feature_array)[0]
                # Convert to 0-1 scale (higher = more anomalous)
                anomaly_score = max(0, min(1, (1 - score) / 2))
            else:
                # Use global model or return moderate score for new users
                anomaly_score = 0.3
            
            return anomaly_score
            
        except Exception as e:
            logger.error(f"Error calculating anomaly score: {str(e)}")
            return 0.0
    
    async def _detect_patterns(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Detect specific behavioral patterns
        """
        patterns = {
            'high_activity': False,
            'unusual_timing': False,
            'data_access_spike': False,
            'login_anomaly': False
        }
        
        # High activity pattern
        if features.get('total_file_accesses', 0) > 100:
            patterns['high_activity'] = True
        
        # Unusual timing pattern
        if features.get('work_hours_ratio', 1) < 0.3:
            patterns['unusual_timing'] = True
        
        # Data access spike
        if features.get('total_data_volume', 0) > 1000000:  # 1MB threshold
            patterns['data_access_spike'] = True
        
        # Login anomaly
        if features.get('login_success_rate', 1) < 0.8:
            patterns['login_anomaly'] = True
        
        return patterns
    
    async def _identify_anomalies(self, features: Dict[str, float], anomaly_score: float) -> List[Dict[str, Any]]:
        """
        Identify specific anomalies in behavior
        """
        anomalies = []
        
        if anomaly_score > 0.7:
            anomalies.append({
                'type': 'high_anomaly_score',
                'severity': 'high',
                'description': f'Overall behavior anomaly score is {anomaly_score:.2f}',
                'features_involved': list(features.keys())
            })
        
        # Check for specific anomalous features
        if features.get('unique_login_locations', 0) > 5:
            anomalies.append({
                'type': 'multiple_locations',
                'severity': 'medium',
                'description': f'User logged in from {features["unique_login_locations"]} different locations',
                'features_involved': ['unique_login_locations']
            })
        
        if features.get('total_data_volume', 0) > 10000000:  # 10MB threshold
            anomalies.append({
                'type': 'large_data_transfer',
                'severity': 'high',
                'description': f'Large data transfer detected: {features["total_data_volume"]:.0f} bytes',
                'features_involved': ['total_data_volume']
            })
        
        return anomalies
    
    def _determine_risk_level(self, anomaly_score: float) -> str:
        """
        Determine risk level based on anomaly score
        """
        if anomaly_score >= 0.8:
            return 'critical'
        elif anomaly_score >= 0.6:
            return 'high'
        elif anomaly_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    async def update_baseline(self, user_id: str, features: List[Dict[str, float]]):
        """
        Update baseline model for a user
        """
        try:
            if len(features) < 10:  # Need minimum data for baseline
                return
            
            # Convert features to DataFrame
            df = pd.DataFrame(features)
            feature_array = df.values
            
            # Fit isolation forest model
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(feature_array)
            
            # Store model for user
            self.baseline_models[user_id] = model
            
            logger.info(f"Updated baseline model for user {user_id} with {len(features)} samples")
            
        except Exception as e:
            logger.error(f"Error updating baseline for user {user_id}: {str(e)}")
