import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import base64
import hmac
import hashlib

logger = logging.getLogger(__name__)

class SplunkIntegration:
    """
    Integration with Splunk Enterprise/Cloud via HTTP Event Collector (HEC)
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8088)
        self.token = config.get('token', '')
        self.index = config.get('index', 'security')
        self.sourcetype = config.get('sourcetype', 'zehraguard:alert')
        self.source = config.get('source', 'zehraguard_insightx')
        self.verify_ssl = config.get('verify_ssl', True)
        self.timeout = config.get('timeout', 30)
        
        self.base_url = f"https://{self.host}:{self.port}"
        if not self.verify_ssl:
            self.base_url = f"http://{self.host}:{self.port}"
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert to Splunk via HEC
        """
        try:
            endpoint = f"{self.base_url}/services/collector/event"
            headers = {
                'Authorization': f'Splunk {self.token}',
                'Content-Type': 'application/json'
            }
            
            # Format event for Splunk
            splunk_event = {
                'time': int(datetime.utcnow().timestamp()),
                'host': 'zehraguard-system',
                'source': self.source,
                'sourcetype': self.sourcetype,
                'index': self.index,
                'event': {
                    'alert_id': alert.get('id'),
                    'user_id': alert.get('user_id'),
                    'threat_type': alert.get('threat_type'),
                    'severity': alert.get('severity'),
                    'risk_score': alert.get('risk_score'),
                    'title': alert.get('title'),
                    'description': alert.get('description'),
                    'evidence': alert.get('evidence', {}),
                    'status': alert.get('status'),
                    'timestamp': alert.get('created_at'),
                    'system': 'ZehraGuard InsightX'
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=splunk_event,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=self.verify_ssl
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('text') == 'Success':
                            logger.info(f"Successfully sent alert {alert.get('id')} to Splunk")
                            return True
                        else:
                            logger.error(f"Splunk returned error: {result}")
                            return False
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send to Splunk: {response.status} - {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending alert to Splunk: {str(e)}")
            return False
    
    async def send_batch_alerts(self, alerts: List[Dict[str, Any]]) -> int:
        """
        Send multiple alerts in batch
        """
        successful = 0
        tasks = []
        
        for alert in alerts:
            task = asyncio.create_task(self.send_alert(alert))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, bool) and result:
                successful += 1
        
        logger.info(f"Sent {successful}/{len(alerts)} alerts to Splunk")
        return successful

class AzureSentinelIntegration:
    """
    Integration with Microsoft Azure Sentinel
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.workspace_id = config.get('workspace_id', '')
        self.shared_key = config.get('shared_key', '')
        self.log_type = config.get('log_type', 'ZehraGuardAlerts')
        self.time_generated_field = config.get('time_generated_field', 'TimeGenerated')
        self.timeout = config.get('timeout', 30)
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert to Azure Sentinel via Data Collector API
        """
        try:
            # Prepare the alert data
            log_data = {
                'AlertId': alert.get('id'),
                'UserId': alert.get('user_id'),
                'ThreatType': alert.get('threat_type'),
                'Severity': alert.get('severity'),
                'RiskScore': alert.get('risk_score'),
                'Title': alert.get('title'),
                'Description': alert.get('description'),
                'Evidence': json.dumps(alert.get('evidence', {})),
                'Status': alert.get('status'),
                'TimeGenerated': alert.get('created_at'),
                'System': 'ZehraGuard InsightX'
            }
            
            # Convert to JSON
            json_data = json.dumps([log_data])
            body = json_data.encode('utf-8')
            
            # Build the signature
            method = 'POST'
            content_type = 'application/json'
            resource = '/api/logs'
            rfc1123date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
            content_length = len(body)
            
            string_to_hash = f"{method}\n{content_length}\n{content_type}\nx-ms-date:{rfc1123date}\n{resource}"
            bytes_to_hash = string_to_hash.encode('utf-8')
            decoded_key = base64.b64decode(self.shared_key)
            encoded_hash = base64.b64encode(
                hmac.new(decoded_key, bytes_to_hash, digestmod=hashlib.sha256).digest()
            ).decode()
            
            authorization = f"SharedKey {self.workspace_id}:{encoded_hash}"
            
            # Build the request
            uri = f"https://{self.workspace_id}.ods.opinsights.azure.com{resource}?api-version=2016-04-01"
            headers = {
                'Content-Type': content_type,
                'Authorization': authorization,
                'Log-Type': self.log_type,
                'x-ms-date': rfc1123date,
                'time-generated-field': self.time_generated_field
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    uri,
                    data=body,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent alert {alert.get('id')} to Azure Sentinel")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send to Azure Sentinel: {response.status} - {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending alert to Azure Sentinel: {str(e)}")
            return False

class QRadarIntegration:
    """
    Integration with IBM QRadar SIEM
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get('host', 'localhost')
        self.api_token = config.get('api_token', '')
        self.verify_ssl = config.get('verify_ssl', True)
        self.timeout = config.get('timeout', 30)
        self.base_url = f"https://{self.host}/api"
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert to QRadar via REST API
        """
        try:
            endpoint = f"{self.base_url}/siem/offenses"
            headers = {
                'SEC': self.api_token,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            # Format offense data for QRadar
            offense_data = {
                'description': f"ZehraGuard Alert: {alert.get('title')}",
                'severity': self._map_severity_to_qradar(alert.get('severity', 'medium')),
                'offense_type': 'Custom Offense',
                'status': 'OPEN',
                'assigned_to': None,
                'follow_up': False,
                'protected': False,
                'source_addresses': [],
                'destination_addresses': [],
                'categories': ['Custom'],
                'custom_properties': {
                    'zehraguard_alert_id': alert.get('id'),
                    'zehraguard_user_id': alert.get('user_id'),
                    'zehraguard_threat_type': alert.get('threat_type'),
                    'zehraguard_risk_score': str(alert.get('risk_score', 0)),
                    'zehraguard_evidence': json.dumps(alert.get('evidence', {}))
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=offense_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=self.verify_ssl
                ) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        logger.info(f"Successfully sent alert {alert.get('id')} to QRadar, offense ID: {result.get('id')}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send to QRadar: {response.status} - {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending alert to QRadar: {str(e)}")
            return False
    
    def _map_severity_to_qradar(self, severity: str) -> int:
        """
        Map ZehraGuard severity to QRadar severity scale (1-10)
        """
        mapping = {
            'low': 3,
            'medium': 5,
            'high': 8,
            'critical': 10
        }
        return mapping.get(severity.lower(), 5)

class WazuhIntegration:
    """
    Integration with Wazuh SIEM
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 55000)
        self.username = config.get('username', 'wazuh')
        self.password = config.get('password', '')
        self.verify_ssl = config.get('verify_ssl', True)
        self.timeout = config.get('timeout', 30)
        self.base_url = f"https://{self.host}:{self.port}"
        self.auth_token = None
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Wazuh API
        """
        try:
            endpoint = f"{self.base_url}/security/user/authenticate"
            auth = aiohttp.BasicAuth(self.username, self.password)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    endpoint,
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=self.verify_ssl
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.auth_token = result['data']['token']
                        logger.info("Successfully authenticated with Wazuh")
                        return True
                    else:
                        logger.error(f"Failed to authenticate with Wazuh: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"Error authenticating with Wazuh: {str(e)}")
            return False
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send alert to Wazuh by creating a custom event
        """
        try:
            if not self.auth_token:
                if not await self.authenticate():
                    return False
            
            # Create custom event in Wazuh
            endpoint = f"{self.base_url}/events"
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'Content-Type': 'application/json'
            }
            
            # Format event for Wazuh
            wazuh_event = {
                'type': 'custom',
                'timestamp': alert.get('created_at'),
                'rule': {
                    'level': self._map_severity_to_level(alert.get('severity', 'medium')),
                    'description': f"ZehraGuard Threat Detection: {alert.get('title')}",
                    'id': f"zehraguard_{alert.get('threat_type', 'unknown')}"
                },
                'agent': {
                    'id': '000',
                    'name': 'zehraguard-system'
                },
                'data': {
                    'alert_id': alert.get('id'),
                    'user_id': alert.get('user_id'),
                    'threat_type': alert.get('threat_type'),
                    'severity': alert.get('severity'),
                    'risk_score': alert.get('risk_score'),
                    'description': alert.get('description'),
                    'evidence': alert.get('evidence', {}),
                    'system': 'ZehraGuard InsightX'
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    json=wazuh_event,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ssl=self.verify_ssl
                ) as response:
                    if response.status in [200, 201]:
                        logger.info(f"Successfully sent alert {alert.get('id')} to Wazuh")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send to Wazuh: {response.status} - {error_text}")
                        return False
            
        except Exception as e:
            logger.error(f"Error sending alert to Wazuh: {str(e)}")
            return False
    
    def _map_severity_to_level(self, severity: str) -> int:
        """
        Map ZehraGuard severity to Wazuh alert level (1-15)
        """
        mapping = {
            'low': 5,
            'medium': 8,
            'high': 12,
            'critical': 15
        }
        return mapping.get(severity.lower(), 8)

class SIEMIntegrationManager:
    """
    Manager for all SIEM integrations
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.integrations = {}
        self.config = config
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """
        Initialize configured SIEM integrations
        """
        if 'splunk' in self.config and self.config['splunk'].get('enabled', False):
            self.integrations['splunk'] = SplunkIntegration(self.config['splunk'])
        
        if 'azure_sentinel' in self.config and self.config['azure_sentinel'].get('enabled', False):
            self.integrations['azure_sentinel'] = AzureSentinelIntegration(self.config['azure_sentinel'])
        
        if 'qradar' in self.config and self.config['qradar'].get('enabled', False):
            self.integrations['qradar'] = QRadarIntegration(self.config['qradar'])
        
        if 'wazuh' in self.config and self.config['wazuh'].get('enabled', False):
            self.integrations['wazuh'] = WazuhIntegration(self.config['wazuh'])
        
        logger.info(f"Initialized {len(self.integrations)} SIEM integrations: {list(self.integrations.keys())}")
    
    async def send_alert_to_all(self, alert: Dict[str, Any]) -> Dict[str, bool]:
        """
        Send alert to all configured SIEM systems
        """
        results = {}
        tasks = []
        
        for siem_name, integration in self.integrations.items():
            task = asyncio.create_task(integration.send_alert(alert))
            tasks.append((siem_name, task))
        
        for siem_name, task in tasks:
            try:
                result = await task
                results[siem_name] = result
            except Exception as e:
                logger.error(f"Error sending to {siem_name}: {str(e)}")
                results[siem_name] = False
        
        successful = sum(1 for success in results.values() if success)
        logger.info(f"Alert {alert.get('id')} sent to {successful}/{len(self.integrations)} SIEM systems")
        
        return results
    
    async def send_batch_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Send batch of alerts to all SIEM systems
        """
        results = {}
        
        for siem_name, integration in self.integrations.items():
            if hasattr(integration, 'send_batch_alerts'):
                results[siem_name] = await integration.send_batch_alerts(alerts)
            else:
                # Fall back to individual sends
                successful = 0
                for alert in alerts:
                    if await integration.send_alert(alert):
                        successful += 1
                results[siem_name] = successful
        
        return results
    
    def get_integration_status(self) -> Dict[str, Any]:
        """
        Get status of all SIEM integrations
        """
        status = {}
        for siem_name, integration in self.integrations.items():
            status[siem_name] = {
                'enabled': True,
                'type': type(integration).__name__,
                'config': self.config.get(siem_name, {})
            }
        
        return status
