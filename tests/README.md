# SHIELD Backend Tests

This directory contains comprehensive tests for the SHIELD backend application.

## Test Structure

```
tests/
├── README.md              # This file
├── conftest.py            # Test configuration and fixtures
├── unit/                  # Unit tests
│   ├── models/           # Tests for Pydantic models
│   ├── core/             # Tests for database clients
│   └── api/              # Tests for FastAPI endpoints
└── integration/          # Integration tests
    ├── test_api_integration.py       # API integration tests
    └── test_database_integration.py  # Database integration tests
```

## Running Tests

### All Tests
```bash
# Using our test runner script
python run_tests.py

# Or using pytest directly
pytest tests/ -v
```

### Unit Tests Only
```bash
pytest tests/unit/ -v
```

### Integration Tests Only
```bash
pytest tests/integration/ -v
```

### With Coverage
```bash
pytest tests/unit/ --cov=app --cov-report=html
```

## Test Categories

### Unit Tests
- **Models**: Test Pydantic model validation, serialization, and business logic
- **Clients**: Test database client methods with mocked MongoDB
- **APIs**: Test FastAPI endpoints with dependency injection mocking

### Integration Tests
- **API Integration**: Full request/response cycle testing
- **Database Integration**: Real MongoDB operations with test database

## Test Dependencies

All test dependencies are managed in `dev-requirements.txt`:
- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `httpx`: HTTP client for API testing
- `pytest-mock`: Mocking utilities
- `mongomock`: MongoDB mocking for unit tests

## Environment Variables

Tests use these environment variables:
- `MONGODB_DB`: Test database name (defaults to "shield_test")
- `SENTRY_DSN`: Sentry configuration (empty for tests)

## CI/CD Integration

Tests are automatically run in GitHub Actions on:
- Push to main, develop, or feature branches
- Pull requests to main or develop branches

The CI pipeline includes:
- Python 3.11, 3.12, and 3.13 testing
- Code linting with ruff
- Security scanning with bandit
- Docker image building and testing

## Writing New Tests

### Model Tests
```python
class TestMyModel:
    def test_model_creation(self):
        model = MyModel(field="value")
        assert model.field == "value"
```

### Client Tests
```python
@pytest.mark.asyncio
async def test_client_method(mock_db):
    client = MyClient()
    client.get_collection = Mock(return_value=mock_db.collection)
    result = client.get_all()
    assert len(result) > 0
```

### API Tests
```python
@pytest.mark.asyncio
async def test_api_endpoint(client, mock_db_client):
    with app.dependency_overrides:
        app.dependency_overrides[get_db] = lambda: mock_db_client
        response = await client.get("/api/endpoint")
        assert response.status_code == 200
```
