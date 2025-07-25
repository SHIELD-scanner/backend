# SHIELD Backend Tests

This directory contains comprehensive tests for the SHIELD backend application.

# SHIELD Backend Tests

This directory contains comprehensive tests for the SHIELD backend application.

## Test Structure

```
tests/
├── README.md              # This file
├── conftest.py            # Test configuration and fixtures
├── unit/                  # Unit tests
│   ├── models/           # Tests for Pydantic models (30 tests ✅)
│   ├── core/             # Tests for database clients (31+ tests ✅)
│   └── api/              # Tests for FastAPI endpoints (partial ⚠️)
└── integration/          # Integration tests
    ├── test_api_integration.py       # API integration tests
    └── test_database_integration.py  # Database integration tests
```

## Test Status

### ✅ Fully Working (84 tests)

- **All Model Tests**: ExposedSecret, Namespace, Pod, SBOM, Vulnerability models
- **Core Client Tests**: ExposeSecret, SBOM, Pod clients
- **Health API**: Basic health endpoint testing

### ⚠️ Partially Working

- **Namespace Client**: Some tests fixed to match `_format_to_namespace` method
- **Pod API**: Updated to use `get_by_name` instead of `get_by_uid`
- **Vulnerability Client**: Uses `get_by_hash` method

### ❌ Not Implemented Yet

- **Application API**: Endpoints return 404 (may not be implemented)
- **Sentry API**: Test endpoints may be internal-only

## Running Tests

### All Tests

```bash
pytest
```

### Unit Tests Only

```bash
pytest tests/unit/
```

### Integration Tests Only

```bash
pytest tests/integration/
```

### With Coverage

```bash
pytest --cov=app --cov-report=term-missing tests/
```

## Test Categories

### Unit Tests

- **Models**: Test Pydantic model validation, serialization, and business logic
- **Core**: Test database clients with mocked dependencies
- **API**: Test individual endpoints with mocked services

### Integration Tests

- **API Integration**: Full request/response cycle testing
- **Database Integration**: Tests requiring actual database connections

## Dependencies

- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for testing FastAPI
- `mongomock`: MongoDB mocking for unit tests

## Environment Variables

- `MONGODB_URI`: Test database connection string
- `MONGODB_DB`: Test database name (defaults to "shield_test")
- `ENV`: Set to "test" for test runs

## Notes

Tests are designed to be independent and can be run in any order. Mock objects are used extensively to isolate units under test from external dependencies.

## Test Status

### ✅ Fully Working (84 tests)

- **All Model Tests**: ExposedSecret, Namespace, Pod, SBOM, Vulnerability models
- **Core Client Tests**: ExposeSecret, SBOM, Pod clients
- **Health API**: Basic health endpoint testing

### ⚠️ Partially Working

- **Namespace Client**: Some tests fixed to match `_format_to_namespace` method
- **Pod API**: Updated to use `get_by_name` instead of `get_by_uid`
- **Vulnerability Client**: Uses `get_by_hash` method

### ❌ Not Implemented Yet

- **Application API**: Endpoints return 404 (may not be implemented)
- **Sentry API**: Test endpoints may be internal-only

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

- Python  3.13 testing
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
