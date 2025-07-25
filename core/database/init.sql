-- ZehraGuard InsightX Database Initialization
-- This script creates the initial database schema

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    manager_id VARCHAR(255),
    start_date TIMESTAMP NOT NULL,
    access_level VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create behavioral profiles table
CREATE TABLE IF NOT EXISTS behavioral_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    profile_data JSONB NOT NULL,
    baseline_established BOOLEAN DEFAULT FALSE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1
);

-- Create threat alerts table
CREATE TABLE IF NOT EXISTS threat_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    threat_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    risk_score DECIMAL(3,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    evidence JSONB,
    false_positive BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create data events table
CREATE TABLE IF NOT EXISTS data_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    source_ip INET,
    user_agent TEXT,
    event_data JSONB NOT NULL,
    risk_score DECIMAL(3,2) DEFAULT 0.0,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ML models table
CREATE TABLE IF NOT EXISTS ml_models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_path VARCHAR(500) NOT NULL,
    performance_metrics JSONB,
    training_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_department ON users(department);
CREATE INDEX IF NOT EXISTS idx_behavioral_profiles_user_id ON behavioral_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_threat_alerts_user_id ON threat_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_threat_alerts_severity ON threat_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_threat_alerts_status ON threat_alerts(status);
CREATE INDEX IF NOT EXISTS idx_threat_alerts_created_at ON threat_alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_data_events_user_id ON data_events(user_id);
CREATE INDEX IF NOT EXISTS idx_data_events_event_type ON data_events(event_type);
CREATE INDEX IF NOT EXISTS idx_data_events_timestamp ON data_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_data_events_processed ON data_events(processed);
CREATE INDEX IF NOT EXISTS idx_ml_models_is_active ON ml_models(is_active);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO users (user_id, username, email, department, role, start_date, access_level, location) VALUES
('user001', 'john.doe', 'john.doe@company.com', 'engineering', 'senior_developer', '2023-01-15', 'standard', 'New York'),
('user002', 'jane.smith', 'jane.smith@company.com', 'finance', 'financial_analyst', '2022-06-01', 'elevated', 'San Francisco'),
('user003', 'mike.wilson', 'mike.wilson@company.com', 'hr', 'hr_manager', '2021-03-10', 'admin', 'Chicago'),
('user004', 'sarah.jones', 'sarah.jones@company.com', 'sales', 'account_manager', '2023-08-20', 'standard', 'Los Angeles'),
('user005', 'admin', 'admin@company.com', 'it', 'system_admin', '2020-01-01', 'super_admin', 'Remote')
ON CONFLICT (user_id) DO NOTHING;
