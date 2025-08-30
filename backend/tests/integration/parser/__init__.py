"""
Parser Module Integration Tests

This package contains comprehensive integration tests for the Parser module including:

Integration Test Categories:
---------------------------

1. Workflow Integration (test_parser_workflow.py)
   - Complete parsing pipeline testing
   - Component interaction verification
   - Data flow validation
   - State management across operations

2. API Integration (test_parser_api.py)
   - HTTP endpoint testing
   - Request/response serialization
   - Error response formatting
   - CORS and content-type validation

3. Performance Integration (test_parser_performance.py)
   - Response time benchmarking
   - Memory usage analysis
   - CPU utilization monitoring
   - Scalability testing

4. Error Recovery Integration (test_parser_error_recovery.py)
   - Network failure recovery
   - API rate limit handling
   - Service degradation recovery
   - Resource exhaustion handling

5. Load Testing Integration (test_parser_load.py)
   - Concurrent request handling
   - Large dataset processing
   - Queue management under load
   - Resource usage patterns

Test Configuration:
------------------

All integration tests use the conftest.py configuration which provides:
- Mock services and clients
- Test data fixtures
- Performance monitoring utilities
- Error simulation tools
- Load testing configurations

Running Integration Tests:
-------------------------

# Run all integration tests
cd /opt/app/backend
poetry run pytest tests/integration/parser/ -v

# Run specific test category
poetry run pytest tests/integration/parser/test_parser_workflow.py -v

# Run with performance profiling
poetry run pytest tests/integration/parser/ --profile-svg

# Run load tests
poetry run pytest tests/integration/parser/test_parser_load.py -v -s

Test Data:
---------

Integration tests use realistic test data including:
- VK API response mocks
- Large datasets for performance testing
- Error scenarios for recovery testing
- Concurrent load patterns

Performance Benchmarks:
----------------------

Integration tests include performance benchmarks:
- Response time < 100ms for single operations
- Memory usage < 100MB increase during load
- CPU utilization < 80% average
- Throughput > 10 operations/second
- Error rate < 5% under normal load

Continuous Integration:
----------------------

These tests are designed to run in CI/CD pipelines and provide:
- Early detection of integration issues
- Performance regression detection
- Scalability validation
- Error handling verification
"""

from .conftest import (
    mock_vk_api_client,
    mock_vk_api_service,
    integration_parser_service,
    sample_vk_api_responses,
    integration_test_data,
    mock_task_storage,
    integration_config,
    setup_integration_environment,
    create_integration_parse_request,
    create_integration_parse_task,
    create_integration_parse_result,
    performance_test_config,
    load_test_config,
    error_simulation_config,
    mock_external_dependencies,
    assert_integration_response_format,
    assert_task_lifecycle,
    assert_performance_metrics,
)

__all__ = [
    # Fixtures
    "mock_vk_api_client",
    "mock_vk_api_service",
    "integration_parser_service",
    "sample_vk_api_responses",
    "integration_test_data",
    "mock_task_storage",
    "integration_config",
    "setup_integration_environment",
    "create_integration_parse_request",
    "create_integration_parse_task",
    "create_integration_parse_result",
    "performance_test_config",
    "load_test_config",
    "error_simulation_config",
    "mock_external_dependencies",
    # Utilities
    "assert_integration_response_format",
    "assert_task_lifecycle",
    "assert_performance_metrics",
]
