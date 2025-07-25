import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import joblib
import tensorflow as tf
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import json
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class MLService:
    """
    Machine Learning service for advanced threat detection and behavioral modeling
    """
    
    def __init__(self, model_path: str = "/app/models"):
        self.model_path = model_path
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.is_initialized = False
        
        # Model configurations
        self.model_configs = {
            'anomaly_detection': {
                'type': 'isolation_forest',
                'params': {
                    'contamination': 0.1,
                    'random_state': 42,
                    'n_estimators': 100
                }
            },
            'threat_classification': {
                'type': 'random_forest',
                'params': {
                    'n_estimators': 200,
                    'random_state': 42,
                    'max_depth': 10,
                    'min_samples_split': 5
                }
            },
            'behavioral_clustering': {
                'type': 'kmeans',
                'params': {
                    'n_clusters': 5,
                    'random_state': 42
                }
            }
        }
    
    async def initialize(self):
        """
        Initialize ML service and load models
        """
        try:
            logger.info("Initializing ML Service...")
            
            # Create model directory if it doesn't exist
            os.makedirs(self.model_path, exist_ok=True)
            
            # Load or train models
            await self._load_or_train_models()
            
            # Initialize feature extractors
            await self._initialize_feature_extractors()
            
            self.is_initialized = True
            logger.info("ML Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ML Service: {str(e)}")
            raise
    
    async def predict_threat_probability(self, user_features: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict threat probability for user features
        """
        try:
            if not self.is_initialized:
                await self.initialize()
            
            # Prepare features
            feature_vector = await self._prepare_features(user_features)
            
            predictions = {}
            
            # Anomaly detection
            if 'anomaly_detection' in self.models:
                anomaly_score = await self._predict_anomaly(feature_vector)
                predictions['anomaly_score'] = float(anomaly_score)
            
            # Threat classification
            if 'threat_classification' in self.models:
                threat_probs = await self._predict_threat_classes(feature_vector)
                predictions.update(threat_probs)
            
            # Risk scoring
            risk_score = await self._calculate_risk_score(predictions)
            predictions['overall_risk_score'] = float(risk_score)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting threat probability: {str(e)}")
            return {'overall_risk_score': 0.0}
    
    async def train_user_baseline(self, user_id: str, historical_data: List[Dict[str, Any]]) -> bool:
        """
        Train personalized baseline model for a user
        """
        try:
            if len(historical_data) < 50:  # Minimum data requirement
                logger.warning(f"Insufficient data to train baseline for user {user_id}")
                return False
            
            logger.info(f"Training baseline model for user {user_id} with {len(historical_data)} samples")
            
            # Prepare training data
            features = []
            for data_point in historical_data:
                feature_vector = await self._extract_features_from_data(data_point)
                if feature_vector:
                    features.append(feature_vector)
            
            if len(features) < 20:
                logger.warning(f"Insufficient valid features for user {user_id}")
                return False
            
            # Train isolation forest for user-specific anomaly detection
            user_model = IsolationForest(
                contamination=0.05,  # Lower contamination for baseline
                random_state=42,
                n_estimators=100
            )
            
            feature_array = np.array(features)
            user_model.fit(feature_array)
            
            # Save user-specific model
            user_model_path = os.path.join(self.model_path, f"user_baseline_{user_id}.joblib")
            joblib.dump(user_model, user_model_path)
            
            logger.info(f"Successfully trained baseline model for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error training user baseline for {user_id}: {str(e)}")
            return False
    
    async def detect_behavioral_drift(self, user_id: str, recent_behavior: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect if user behavior has drifted from baseline
        """
        try:
            user_model_path = os.path.join(self.model_path, f"user_baseline_{user_id}.joblib")
            
            if not os.path.exists(user_model_path):
                return {
                    'drift_detected': False,
                    'drift_score': 0.0,
                    'reason': 'No baseline model available'
                }
            
            # Load user model
            user_model = joblib.load(user_model_path)
            
            # Prepare recent behavior features
            feature_vector = await self._prepare_features(recent_behavior)
            feature_array = np.array(feature_vector).reshape(1, -1)
            
            # Calculate anomaly score
            anomaly_score = user_model.decision_function(feature_array)[0]
            
            # Convert to drift score (0-1, higher = more drift)
            drift_score = max(0, min(1, (1 - anomaly_score) / 2))
            
            # Determine if drift is significant
            drift_threshold = 0.7
            drift_detected = drift_score > drift_threshold
            
            return {
                'drift_detected': drift_detected,
                'drift_score': float(drift_score),
                'reason': 'Significant deviation from baseline' if drift_detected else 'Behavior within normal range',
                'threshold': drift_threshold
            }
            
        except Exception as e:
            logger.error(f"Error detecting behavioral drift for user {user_id}: {str(e)}")
            return {
                'drift_detected': False,
                'drift_score': 0.0,
                'reason': f'Error: {str(e)}'
            }
    
    async def update_threat_models(self, training_data: List[Dict[str, Any]], labels: List[str]) -> bool:
        """
        Update threat detection models with new training data
        """
        try:
            logger.info(f"Updating threat models with {len(training_data)} samples")
            
            if len(training_data) < 100:
                logger.warning("Insufficient data for model training")
                return False
            
            # Prepare training data
            features = []
            for data_point in training_data:
                feature_vector = await self._extract_features_from_data(data_point)
                if feature_vector:
                    features.append(feature_vector)
            
            if len(features) != len(labels):
                logger.error("Mismatch between features and labels")
                return False
            
            feature_array = np.array(features)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                feature_array, labels, test_size=0.2, random_state=42, stratify=labels
            )
            
            # Train threat classification model
            classifier = RandomForestClassifier(**self.model_configs['threat_classification']['params'])
            classifier.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = classifier.predict(X_test)
            accuracy = np.mean(y_pred == y_test)
            
            logger.info(f"Model training completed. Accuracy: {accuracy:.3f}")
            
            # Save updated model
            model_path = os.path.join(self.model_path, "threat_classification.joblib")
            joblib.dump(classifier, model_path)
            
            # Update in-memory model
            self.models['threat_classification'] = classifier
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating threat models: {str(e)}")
            return False
    
    async def analyze_feature_importance(self, model_name: str) -> Dict[str, float]:
        """
        Analyze feature importance for interpretability
        """
        try:
            if model_name not in self.models:
                return {}
            
            model = self.models[model_name]
            
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                
                feature_importance = {}
                for i, importance in enumerate(importances):
                    if i < len(self.feature_columns):
                        feature_importance[self.feature_columns[i]] = float(importance)
                
                # Sort by importance
                sorted_features = dict(sorted(feature_importance.items(), 
                                            key=lambda x: x[1], reverse=True))
                
                return sorted_features
            
            return {}
            
        except Exception as e:
            logger.error(f"Error analyzing feature importance: {str(e)}")
            return {}
    
    async def predict_risk_trajectory(self, user_id: str, time_series_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Predict risk trajectory over time
        """
        try:
            if len(time_series_data) < 10:
                return {
                    'predicted_risk': 0.0,
                    'trend': 'stable',
                    'confidence': 0.0
                }
            
            # Extract risk scores over time
            risk_scores = []
            timestamps = []
            
            for data_point in time_series_data:
                features = await self._prepare_features(data_point.get('features', {}))
                risk_score = await self._calculate_risk_score({'overall_risk_score': 0.0})
                
                risk_scores.append(risk_score)
                timestamps.append(data_point.get('timestamp', datetime.utcnow().isoformat()))
            
            # Simple trend analysis
            if len(risk_scores) >= 3:
                recent_trend = np.mean(risk_scores[-3:]) - np.mean(risk_scores[:-3])
                
                if recent_trend > 0.1:
                    trend = 'increasing'
                elif recent_trend < -0.1:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Predict next risk score (simple linear extrapolation)
            if len(risk_scores) >= 2:
                slope = (risk_scores[-1] - risk_scores[-2])
                predicted_risk = max(0.0, min(1.0, risk_scores[-1] + slope))
            else:
                predicted_risk = risk_scores[-1] if risk_scores else 0.0
            
            confidence = min(1.0, len(risk_scores) / 20.0)  # Higher confidence with more data
            
            return {
                'predicted_risk': float(predicted_risk),
                'trend': trend,
                'confidence': float(confidence),
                'historical_scores': risk_scores[-10:],  # Last 10 scores
                'trend_magnitude': float(abs(recent_trend)) if len(risk_scores) >= 3 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Error predicting risk trajectory: {str(e)}")
            return {
                'predicted_risk': 0.0,
                'trend': 'stable',
                'confidence': 0.0
            }
    
    # Private helper methods
    
    async def _load_or_train_models(self):
        """
        Load existing models or train new ones
        """
        try:
            # Try to load existing models
            for model_name in self.model_configs.keys():
                model_path = os.path.join(self.model_path, f"{model_name}.joblib")
                
                if os.path.exists(model_path):
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"Loaded existing model: {model_name}")
                else:
                    # Train new model with dummy data for initialization
                    await self._train_initial_model(model_name)
            
        except Exception as e:
            logger.error(f"Error loading/training models: {str(e)}")
            raise
    
    async def _train_initial_model(self, model_name: str):
        """
        Train initial model with synthetic data
        """
        try:
            model_config = self.model_configs[model_name]
            
            if model_config['type'] == 'isolation_forest':
                # Generate synthetic normal behavior data
                synthetic_data = self._generate_synthetic_data(1000)
                
                model = IsolationForest(**model_config['params'])
                model.fit(synthetic_data)
                
                self.models[model_name] = model
                
                # Save model
                model_path = os.path.join(self.model_path, f"{model_name}.joblib")
                joblib.dump(model, model_path)
                
                logger.info(f"Trained initial {model_name} model")
            
            elif model_config['type'] == 'random_forest':
                # Generate synthetic labeled data
                synthetic_data, synthetic_labels = self._generate_synthetic_labeled_data(1000)
                
                model = RandomForestClassifier(**model_config['params'])
                model.fit(synthetic_data, synthetic_labels)
                
                self.models[model_name] = model
                
                # Save model
                model_path = os.path.join(self.model_path, f"{model_name}.joblib")
                joblib.dump(model, model_path)
                
                logger.info(f"Trained initial {model_name} model")
            
        except Exception as e:
            logger.error(f"Error training initial model {model_name}: {str(e)}")
            raise
    
    def _generate_synthetic_data(self, n_samples: int) -> np.ndarray:
        """
        Generate synthetic behavioral data for model initialization
        """
        np.random.seed(42)
        
        # Define feature ranges for normal behavior
        features = []
        
        for _ in range(n_samples):
            sample = [
                np.random.normal(100, 20),    # avg_dwell_time
                np.random.normal(50, 10),     # avg_flight_time
                np.random.normal(200, 40),    # avg_typing_speed
                np.random.normal(150, 30),    # avg_mouse_velocity
                np.random.randint(5, 50),     # total_file_accesses
                np.random.randint(1, 10),     # unique_applications
                np.random.uniform(0.6, 1.0),  # work_hours_ratio
                np.random.randint(1, 3),      # unique_login_locations
                np.random.uniform(0.8, 1.0),  # login_success_rate
                np.random.uniform(0, 1000000) # total_data_volume
            ]
            features.append(sample)
        
        self.feature_columns = [
            'avg_dwell_time', 'avg_flight_time', 'avg_typing_speed',
            'avg_mouse_velocity', 'total_file_accesses', 'unique_applications',
            'work_hours_ratio', 'unique_login_locations', 'login_success_rate',
            'total_data_volume'
        ]
        
        return np.array(features)
    
    def _generate_synthetic_labeled_data(self, n_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic labeled data for classification
        """
        data = self._generate_synthetic_data(n_samples)
        
        # Generate labels based on simple rules
        labels = []
        for sample in data:
            if sample[9] > 5000000 or sample[6] < 0.3:  # High data volume or low work hours
                labels.append('high_risk')
            elif sample[8] < 0.7 or sample[7] > 5:  # Low login success or many locations
                labels.append('medium_risk')
            else:
                labels.append('low_risk')
        
        return data, np.array(labels)
    
    async def _initialize_feature_extractors(self):
        """
        Initialize feature extraction components
        """
        try:
            # Initialize scalers if not loaded
            if 'standard_scaler' not in self.scalers:
                scaler = StandardScaler()
                # Fit with synthetic data
                synthetic_data = self._generate_synthetic_data(100)
                scaler.fit(synthetic_data)
                self.scalers['standard_scaler'] = scaler
            
            # Initialize encoders
            if 'label_encoder' not in self.encoders:
                encoder = LabelEncoder()
                encoder.fit(['low_risk', 'medium_risk', 'high_risk'])
                self.encoders['label_encoder'] = encoder
            
        except Exception as e:
            logger.error(f"Error initializing feature extractors: {str(e)}")
            raise
    
    async def _prepare_features(self, user_features: Dict[str, Any]) -> np.ndarray:
        """
        Prepare features for model input
        """
        try:
            # Extract known features in correct order
            feature_vector = []
            
            for feature_name in self.feature_columns:
                value = user_features.get(feature_name, 0.0)
                feature_vector.append(float(value))
            
            # Scale features
            if 'standard_scaler' in self.scalers:
                feature_array = np.array(feature_vector).reshape(1, -1)
                scaled_features = self.scalers['standard_scaler'].transform(feature_array)
                return scaled_features[0]
            
            return np.array(feature_vector)
            
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            return np.zeros(len(self.feature_columns))
    
    async def _extract_features_from_data(self, data_point: Dict[str, Any]) -> Optional[List[float]]:
        """
        Extract features from raw data point
        """
        try:
            # This would extract features from the raw behavioral data
            # For now, return dummy features
            features = []
            
            event_data = data_point.get('event_data', {})
            
            # Extract basic features
            features.extend([
                event_data.get('dwell_time', 100.0),
                event_data.get('flight_time', 50.0),
                event_data.get('typing_speed', 200.0),
                event_data.get('mouse_velocity', 150.0),
                len(event_data.get('file_accesses', [])),
                len(event_data.get('applications', [])),
                event_data.get('work_hours_ratio', 0.8),
                len(event_data.get('login_locations', [])),
                event_data.get('login_success_rate', 1.0),
                event_data.get('data_volume', 0.0)
            ])
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features from data: {str(e)}")
            return None
    
    async def _predict_anomaly(self, feature_vector: np.ndarray) -> float:
        """
        Predict anomaly score
        """
        try:
            model = self.models.get('anomaly_detection')
            if model is None:
                return 0.0
            
            # Reshape if necessary
            if len(feature_vector.shape) == 1:
                feature_vector = feature_vector.reshape(1, -1)
            
            # Get decision function score
            score = model.decision_function(feature_vector)[0]
            
            # Convert to 0-1 scale (higher = more anomalous)
            anomaly_score = max(0, min(1, (1 - score) / 2))
            
            return anomaly_score
            
        except Exception as e:
            logger.error(f"Error predicting anomaly: {str(e)}")
            return 0.0
    
    async def _predict_threat_classes(self, feature_vector: np.ndarray) -> Dict[str, float]:
        """
        Predict threat class probabilities
        """
        try:
            model = self.models.get('threat_classification')
            if model is None:
                return {}
            
            # Reshape if necessary
            if len(feature_vector.shape) == 1:
                feature_vector = feature_vector.reshape(1, -1)
            
            # Get class probabilities
            probabilities = model.predict_proba(feature_vector)[0]
            classes = model.classes_
            
            # Map to threat types
            threat_probs = {}
            for i, class_name in enumerate(classes):
                threat_probs[f"{class_name}_probability"] = float(probabilities[i])
            
            return threat_probs
            
        except Exception as e:
            logger.error(f"Error predicting threat classes: {str(e)}")
            return {}
    
    async def _calculate_risk_score(self, predictions: Dict[str, float]) -> float:
        """
        Calculate overall risk score from predictions
        """
        try:
            # Weighted combination of different scores
            anomaly_score = predictions.get('anomaly_score', 0.0)
            high_risk_prob = predictions.get('high_risk_probability', 0.0)
            medium_risk_prob = predictions.get('medium_risk_probability', 0.0)
            
            # Weighted average
            risk_score = (
                anomaly_score * 0.4 +
                high_risk_prob * 0.4 +
                medium_risk_prob * 0.2
            )
            
            return min(1.0, max(0.0, risk_score))
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 0.0
