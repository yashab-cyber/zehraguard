# ZehraGuard InsightX Test Suite

This directory contains comprehensive tests for the ZehraGuard InsightX platform.

## Test Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for service interactions
- `e2e/` - End-to-end tests for complete workflows
- `performance/` - Performance and load tests
- `security/` - Security and penetration tests

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=core --cov-report=html

# Run performance tests
pytest tests/performance/ --benchmark-only
```

## Test Data

Use the test data generator to create realistic test scenarios:

```bash
python scripts/generate_test_data.py
```
