# Settings Module Tests

This directory contains comprehensive unit and integration tests for the Settings module.

## Test Structure

```
tests/unit/settings/
├── __init__.py
├── conftest.py              # Shared test fixtures and configuration
├── pytest.ini              # Pytest configuration
├── run_tests.py            # Test runner script
├── test_service.py         # SettingsService tests
├── test_repository.py      # SettingsRepository tests
├── test_router.py          # Router endpoint tests
├── test_config.py          # SettingsConfig tests
├── test_utils_schemas_exceptions_constants.py  # Utils, schemas, exceptions, constants tests
├── test_integration.py     # Integration tests
└── README.md              # This file
```

## Test Coverage

The test suite covers:

### Unit Tests

- **SettingsService**: Business logic, validation, error handling
- **SettingsRepository**: Data persistence, caching, validation
- **Router Endpoints**: HTTP request/response handling
- **SettingsConfig**: Configuration management
- **Utilities**: Helper functions, validation, data transformation
- **Schemas**: Pydantic models validation
- **Exceptions**: Custom exception handling
- **Constants**: Configuration constants
- **Dependencies**: FastAPI dependency injection

### Integration Tests

- End-to-end request/response cycles
- Service-repository interactions
- Router-service integration
- Error propagation across layers
- Concurrent operations
- Performance testing
- Resource cleanup

## Running Tests

### Prerequisites

Make sure you have the required dependencies installed:

```bash
# With Poetry (recommended)
poetry install

# Or with pip
pip install pytest pytest-asyncio pytest-cov pytest-xdist fastapi pydantic
```

### Quick Start

```bash
# Run all tests
python run_tests.py

# Run with Poetry
python run_tests.py --poetry

# Run with verbose output
python run_tests.py -v

# Run with coverage report
python run_tests.py --coverage
```

### Test Selection

```bash
# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run only performance tests
python run_tests.py --performance

# Include slow tests
python run_tests.py --slow

# Run specific test file
python run_tests.py --test-file test_service.py

# Run specific test function
python run_tests.py --test-function test_get_current_settings
```

### Advanced Options

```bash
# Run tests in parallel
python run_tests.py --parallel 4

# Stop on first failure
python run_tests.py --fail-fast

# Generate HTML coverage report
python run_tests.py --coverage

# Clean test artifacts
python run_tests.py --clean

# Check dependencies
python run_tests.py --check-deps
```

### Using Poetry

```bash
# Run all tests with Poetry
poetry run python run_tests.py

# Or directly with pytest
poetry run pytest tests/unit/settings/

# With coverage
poetry run pytest --cov=src.settings tests/unit/settings/
```

## Test Configuration

### Pytest Configuration

The `pytest.ini` file contains the test configuration:

```ini
[tool:pytest]
testpaths = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
    --asyncio-mode=auto
markers =
    performance: marks tests as performance tests
    integration: marks tests as integration tests
    slow: marks tests as slow (deselect with '-m "not slow"')
```

### Test Markers

- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests

## Test Fixtures

### Shared Fixtures (conftest.py)

- `sample_settings_data`: Sample settings for testing
- `sample_section_data`: Sample section data
- `sample_invalid_data`: Invalid data for validation testing
- `mock_settings_repository`: Mock repository
- `mock_settings_service`: Mock service
- `mock_request`: Mock FastAPI request
- `mock_database_session`: Mock database session
- `performance_timer`: Performance measurement
- `validation_errors`: Sample validation errors
- `health_check_response`: Sample health check response

### Custom Generators

- `generate_test_settings`: Generate test settings data
- `generate_large_settings`: Generate large settings for performance testing
- `simulate_repository_error`: Simulate repository errors

## Writing New Tests

### Test File Structure

```python
import pytest
from src.settings.module import ClassToTest

class TestClassToTest:
    """Test suite for ClassToTest"""

    @pytest.fixture
    def setup_fixture(self):
        """Setup fixture for tests"""
        return ClassToTest()

    def test_example_test(self, setup_fixture):
        """Test example functionality"""
        # Arrange
        instance = setup_fixture

        # Act
        result = instance.method()

        # Assert
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_async_example_test(self, setup_fixture):
        """Test async functionality"""
        # Arrange
        instance = setup_fixture

        # Act
        result = await instance.async_method()

        # Assert
        assert result == expected_value
```

### Mocking Best Practices

```python
@pytest.fixture
def mock_dependency(self):
    """Create mock dependency"""
    mock = Mock(spec=DependencyClass)
    mock.method = AsyncMock(return_value=expected_value)
    return mock

def test_with_mock(self, mock_dependency):
    """Test using mock dependency"""
    # Use mock_dependency in your test
    pass
```

## Coverage Requirements

The test suite aims for:

- **Unit Tests**: >90% coverage
- **Integration Tests**: Key user journeys covered
- **Performance Tests**: Critical paths tested under load

## Continuous Integration

The tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Settings Tests
  run: |
    cd backend
    python tests/unit/settings/run_tests.py --coverage --parallel 2
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running tests from the correct directory
2. **Async Test Issues**: Ensure pytest-asyncio is installed and configured
3. **Coverage Issues**: Check that source files are properly included
4. **Mock Errors**: Verify mock specifications match the actual interfaces

### Debugging Tests

```bash
# Run with detailed output
python run_tests.py -v -s

# Run specific failing test
python run_tests.py --test-function failing_test_name

# Run with debugger
python -m pytest tests/unit/settings/test_file.py::TestClass::test_method -s --pdb
```

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Add appropriate docstrings
3. Use fixtures for common setup
4. Include both positive and negative test cases
5. Add integration tests for new features
6. Update this README if adding new test categories

## Test Data

Test data is provided through fixtures and can be extended in `conftest.py`. For large datasets, consider creating separate data files in a `data/` subdirectory.

## Performance Testing

Performance tests use the `@pytest.mark.performance` marker and measure:

- Response times
- Memory usage
- Concurrent request handling
- Resource cleanup

Run performance tests with:

```bash
python run_tests.py --performance --slow
```
