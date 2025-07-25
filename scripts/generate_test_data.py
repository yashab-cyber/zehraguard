"""
ZehraGuard InsightX Test Data Generator
Generates realistic behavioral data for testing and demonstration
"""

import asyncio
import random
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np

class TestDataGenerator:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.users = []
        self.data_types = [
            'keystroke', 'mouse_movement', 'file_access', 
            'network_request', 'login_event', 'application_usage'
        ]
    
    def generate_test_users(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate test user profiles"""
        departments = ['engineering', 'finance', 'hr', 'sales', 'marketing', 'operations']
        roles = ['developer', 'analyst', 'manager', 'director', 'specialist', 'coordinator']
        locations = ['New York', 'San Francisco', 'Chicago', 'Boston', 'Austin', 'Remote']
        
        users = []
        for i in range(count):
            user = {
                'user_id': f'test_user_{i:03d}',
                'username': f'test.user{i:03d}',
                'email': f'test.user{i:03d}@company.com',
                'department': random.choice(departments),
                'role': random.choice(roles),
                'start_date': (datetime.now() - timedelta(days=random.randint(30, 1000))).isoformat(),
                'access_level': random.choice(['standard', 'elevated', 'admin']),
                'location': random.choice(locations)
            }
            users.append(user)
        
        self.users = users
        return users
    
    def generate_keystroke_data(self, user_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate realistic keystroke dynamics data"""
        return {
            'user_id': user_id,
            'event_type': 'keystroke',
            'timestamp': timestamp.isoformat(),
            'event_data': {
                'dwell_time': random.normalvariate(80, 20),  # milliseconds
                'flight_time': random.normalvariate(60, 15),
                'typing_speed': random.normalvariate(180, 40),  # characters per minute
                'key_sequence': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)),
                'pressure': random.uniform(0.3, 0.8),
                'session_id': f'session_{random.randint(1000, 9999)}'
            }
        }
    
    def generate_mouse_data(self, user_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate mouse movement data"""
        return {
            'user_id': user_id,
            'event_type': 'mouse_movement',
            'timestamp': timestamp.isoformat(),
            'event_data': {
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'velocity': random.normalvariate(150, 50),
                'acceleration': random.normalvariate(25, 10),
                'click_type': random.choice(['left', 'right', 'middle', 'move']),
                'pressure': random.uniform(0.0, 1.0) if random.random() > 0.7 else 0.0
            }
        }
    
    def generate_file_access_data(self, user_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate file access event data"""
        file_types = ['.txt', '.doc', '.pdf', '.xls', '.ppt', '.jpg', '.png', '.mp4']
        access_types = ['read', 'write', 'delete', 'copy', 'move']
        
        return {
            'user_id': user_id,
            'event_type': 'file_access',
            'timestamp': timestamp.isoformat(),
            'event_data': {
                'file_path': f'/home/{user_id}/documents/file_{random.randint(1, 1000)}{random.choice(file_types)}',
                'access_type': random.choice(access_types),
                'file_size': random.randint(1024, 10485760),  # 1KB to 10MB
                'file_type': random.choice(file_types)[1:],
                'process_name': random.choice(['notepad.exe', 'word.exe', 'excel.exe', 'browser.exe']),
                'duration': random.randint(1, 300)  # seconds
            }
        }
    
    def generate_network_data(self, user_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate network request data"""
        domains = [
            'google.com', 'github.com', 'stackoverflow.com', 'company.com',
            'gmail.com', 'linkedin.com', 'aws.amazon.com', 'dropbox.com'
        ]
        protocols = ['HTTP', 'HTTPS', 'FTP', 'SSH']
        
        return {
            'user_id': user_id,
            'event_type': 'network_request',
            'timestamp': timestamp.isoformat(),
            'event_data': {
                'destination_ip': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                'destination_port': random.choice([80, 443, 22, 21, 993, 587]),
                'protocol': random.choice(protocols),
                'data_volume': random.randint(1024, 1048576),  # 1KB to 1MB
                'domain': random.choice(domains),
                'request_type': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
    
    def generate_login_data(self, user_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate login event data"""
        return {
            'user_id': user_id,
            'event_type': 'login_event',
            'timestamp': timestamp.isoformat(),
            'event_data': {
                'success': random.random() > 0.05,  # 95% success rate
                'location': random.choice(['New York, NY', 'San Francisco, CA', 'Chicago, IL', 'Remote']),
                'device_id': f'device_{random.randint(100, 999)}',
                'ip_address': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'authentication_method': random.choice(['password', 'mfa', 'sso'])
            }
        }
    
    def generate_app_usage_data(self, user_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate application usage data"""
        applications = [
            'Microsoft Word', 'Excel', 'PowerPoint', 'Outlook', 'Chrome',
            'Slack', 'Zoom', 'VS Code', 'Photoshop', 'Terminal'
        ]
        
        return {
            'user_id': user_id,
            'event_type': 'application_usage',
            'timestamp': timestamp.isoformat(),
            'event_data': {
                'application': random.choice(applications),
                'duration': random.randint(60, 3600),  # 1 minute to 1 hour
                'window_title': f'Document_{random.randint(1, 100)}',
                'idle_time': random.randint(0, 300),
                'active_time': random.randint(60, 3600)
            }
        }
    
    def generate_anomalous_data(self, user_id: str, timestamp: datetime) -> Dict[str, Any]:
        """Generate anomalous behavior data for testing detection"""
        anomaly_type = random.choice(['excessive_data_access', 'unusual_timing', 'failed_logins'])
        
        if anomaly_type == 'excessive_data_access':
            return {
                'user_id': user_id,
                'event_type': 'file_access',
                'timestamp': timestamp.isoformat(),
                'event_data': {
                    'file_path': f'/confidential/sensitive_data_{random.randint(1, 100)}.xlsx',
                    'access_type': 'read',
                    'file_size': random.randint(50000000, 100000000),  # 50-100MB (large)
                    'file_type': 'xlsx',
                    'process_name': 'unknown_process.exe',
                    'duration': random.randint(1800, 3600)  # 30-60 minutes
                }
            }
        elif anomaly_type == 'unusual_timing':
            # Generate activity during off-hours (midnight to 6 AM)
            off_hours_time = timestamp.replace(hour=random.randint(0, 5))
            return self.generate_file_access_data(user_id, off_hours_time)
        else:  # failed_logins
            return {
                'user_id': user_id,
                'event_type': 'login_event',
                'timestamp': timestamp.isoformat(),
                'event_data': {
                    'success': False,
                    'location': 'Unknown Location',
                    'device_id': f'suspicious_device_{random.randint(1, 10)}',
                    'ip_address': f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}',
                    'user_agent': 'Suspicious User Agent',
                    'authentication_method': 'brute_force_attempt'
                }
            }
    
    async def create_users_via_api(self):
        """Create test users via API"""
        print("Creating test users...")
        for user in self.users:
            try:
                response = requests.post(f"{self.api_base_url}/api/v1/users", json=user)
                if response.status_code == 200:
                    print(f"✓ Created user: {user['user_id']}")
                else:
                    print(f"✗ Failed to create user {user['user_id']}: {response.text}")
            except Exception as e:
                print(f"✗ Error creating user {user['user_id']}: {str(e)}")
    
    async def generate_behavioral_data_batch(self, days: int = 7, events_per_day: int = 100):
        """Generate a batch of behavioral data"""
        print(f"Generating {days} days of behavioral data...")
        
        all_events = []
        start_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            print(f"Generating data for {current_date.strftime('%Y-%m-%d')}")
            
            for _ in range(events_per_day):
                user = random.choice(self.users)
                user_id = user['user_id']
                
                # Random time during the day (with bias toward work hours)
                if random.random() < 0.8:  # 80% during work hours
                    hour = random.randint(9, 17)
                else:  # 20% outside work hours
                    hour = random.choice(list(range(0, 9)) + list(range(18, 24)))
                
                event_time = current_date.replace(
                    hour=hour,
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                )
                
                # Generate different types of events
                data_type = random.choice(self.data_types)
                
                if data_type == 'keystroke':
                    event = self.generate_keystroke_data(user_id, event_time)
                elif data_type == 'mouse_movement':
                    event = self.generate_mouse_data(user_id, event_time)
                elif data_type == 'file_access':
                    event = self.generate_file_access_data(user_id, event_time)
                elif data_type == 'network_request':
                    event = self.generate_network_data(user_id, event_time)
                elif data_type == 'login_event':
                    event = self.generate_login_data(user_id, event_time)
                else:  # application_usage
                    event = self.generate_app_usage_data(user_id, event_time)
                
                # Occasionally inject anomalous data (5% chance)
                if random.random() < 0.05:
                    event = self.generate_anomalous_data(user_id, event_time)
                
                all_events.append(event)
        
        return all_events
    
    async def send_events_to_api(self, events: List[Dict[str, Any]], batch_size: int = 100):
        """Send events to the API in batches"""
        print(f"Sending {len(events)} events to API...")
        
        for i in range(0, len(events), batch_size):
            batch = events[i:i+batch_size]
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/api/v1/behavioral-data",
                    json={'data': batch}
                )
                
                if response.status_code == 200:
                    print(f"✓ Sent batch {i//batch_size + 1}/{(len(events) + batch_size - 1)//batch_size}")
                else:
                    print(f"✗ Failed to send batch: {response.text}")
            
            except Exception as e:
                print(f"✗ Error sending batch: {str(e)}")
            
            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.1)

async def main():
    """Main test data generation function"""
    print("🧪 ZehraGuard InsightX Test Data Generator")
    print("=" * 50)
    
    generator = TestDataGenerator()
    
    # Generate test users
    users = generator.generate_test_users(count=20)
    print(f"Generated {len(users)} test users")
    
    # Create users via API
    await generator.create_users_via_api()
    
    # Generate behavioral data
    events = await generator.generate_behavioral_data_batch(days=14, events_per_day=200)
    print(f"Generated {len(events)} behavioral events")
    
    # Send events to API
    await generator.send_events_to_api(events)
    
    print("\n✅ Test data generation complete!")
    print("\n📊 You can now:")
    print("1. View the dashboard at http://localhost:3000")
    print("2. Check alerts in the API at http://localhost:8000/api/v1/threats/alerts")
    print("3. Monitor behavioral patterns for the test users")

if __name__ == "__main__":
    asyncio.run(main())
