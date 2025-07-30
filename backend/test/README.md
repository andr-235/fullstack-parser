# NestJS Backend Testing Documentation

## Overview

This directory contains comprehensive testing infrastructure for the NestJS backend, including integration tests, performance tests, and data consistency verification.

## Test Structure

### Integration Tests (E2E)

#### `users.e2e-spec.ts`
- **Purpose**: End-to-end testing of User module functionality
- **Coverage**: 
  - User CRUD operations (Create, Read, Update, Delete)
  - Input validation and error handling
  - Pagination and search functionality
  - Duplicate email handling
  - Field validation (email format, required fields)

#### `parser.e2e-spec.ts`
- **Purpose**: End-to-end testing of Parser module and VK API integration
- **Coverage**:
  - VK group parsing functionality
  - VK post parsing with statistics
  - Parser health checks
  - Keyword-based parsing
  - Error handling for invalid inputs
  - Rate limiting and API error scenarios

#### `keywords.e2e-spec.ts`
- **Purpose**: End-to-end testing of Keywords module
- **Coverage**:
  - Keyword CRUD operations
  - Bulk keyword creation
  - Search and filtering functionality
  - Statistics and analytics
  - Duplicate handling
  - Keyword matching with comments

#### `comments.e2e-spec.ts`
- **Purpose**: End-to-end testing of Comments module
- **Coverage**:
  - Comment CRUD operations
  - Search and filtering by text, group, post
  - Statistics and analytics
  - Keyword matching functionality
  - Pagination and sorting

#### `groups.e2e-spec.ts`
- **Purpose**: End-to-end testing of Groups module
- **Coverage**:
  - Group CRUD operations
  - Bulk group creation
  - Search and filtering
  - Statistics and analytics
  - Post relationships
  - Duplicate VK ID handling

#### `performance.e2e-spec.ts`
- **Purpose**: Performance and load testing
- **Coverage**:
  - Bulk operations performance
  - Search performance with large datasets
  - Statistics calculation performance
  - Concurrent request handling
  - Memory usage monitoring
  - Response time validation

### Data Consistency Verification

#### `verify-data-consistency.ts`
- **Purpose**: Comprehensive data integrity verification
- **Coverage**:
  - Foreign key relationship validation
  - Data integrity constraint checking
  - Duplicate detection
  - Statistical consistency verification
  - Data anomaly detection
  - Referential integrity validation

## Test Configuration

### Jest Configuration

#### Unit Tests (`package.json`)
```json
{
  "jest": {
    "moduleFileExtensions": ["js", "json", "ts"],
    "rootDir": "src",
    "testRegex": ".*\\.spec\\.ts$",
    "transform": {
      "^.+\\.(t|j)s$": "ts-jest"
    },
    "collectCoverageFrom": ["**/*.(t|j)s"],
    "coverageDirectory": "../coverage",
    "testEnvironment": "node"
  }
}
```

#### E2E Tests (`test/jest-e2e.json`)
```json
{
  "moduleFileExtensions": ["js", "json", "ts"],
  "rootDir": ".",
  "testEnvironment": "node",
  "testRegex": ".e2e-spec.ts$",
  "transform": {
    "^.+\\.(t|j)s$": "ts-jest"
  },
  "moduleNameMapping": {
    "^src/(.*)$": "<rootDir>/../src/$1"
  }
}
```

## Running Tests

### Automated Test Runner

Use the provided test runner script for comprehensive testing:

```bash
cd backend
./test/run-tests.sh
```

This script will:
1. Install dependencies if needed
2. Generate Prisma client
3. Run database migrations
4. Execute unit tests
5. Execute E2E integration tests
6. Execute performance tests
7. Generate coverage reports

### Manual Test Execution

#### Unit Tests
```bash
npm run test
```

#### E2E Tests
```bash
npm run test:e2e
```

#### Performance Tests
```bash
npm run test:e2e -- --testPathPattern=performance.e2e-spec.ts
```

#### Coverage Report
```bash
npm run test:cov
```

#### Data Consistency Verification
```bash
npx ts-node test/verify-data-consistency.ts
```

## Test Data Management

### Database Cleanup

Each test suite includes proper database cleanup:

```typescript
beforeEach(async () => {
  // Clean up database before each test
  await prisma.commentKeywordMatch.deleteMany();
  await prisma.vKComment.deleteMany();
  await prisma.vKPost.deleteMany();
  await prisma.vKGroup.deleteMany();
  await prisma.keyword.deleteMany();
  await prisma.user.deleteMany();
});
```

### Test Data Creation

Tests create realistic test data for comprehensive coverage:

```typescript
// Create test data
await prisma.vKGroup.createMany({
  data: [
    { vkId: 11111, screenName: 'group1', name: 'Test Group 1' },
    { vkId: 22222, screenName: 'group2', name: 'Test Group 2' }
  ]
});
```

## Performance Benchmarks

### Response Time Requirements

- **CRUD Operations**: < 500ms
- **Search Operations**: < 1000ms
- **Bulk Operations**: < 5000ms for 100 items
- **Statistics Calculation**: < 2000ms
- **Concurrent Requests**: < 3000ms for 6 concurrent requests

### Memory Usage Requirements

- **Bulk Operations**: < 50MB memory increase
- **Search Operations**: < 100MB peak memory
- **Statistics Operations**: < 200MB peak memory

## Test Coverage Requirements

### Minimum Coverage Targets

- **Unit Tests**: 80% line coverage
- **Integration Tests**: 90% API endpoint coverage
- **Error Scenarios**: 100% error handling coverage
- **Data Validation**: 100% validation rule coverage

### Coverage Areas

1. **API Endpoints**: All CRUD operations, search, filtering, statistics
2. **Business Logic**: Keyword matching, data processing, validation
3. **Error Handling**: Invalid inputs, database errors, API failures
4. **Performance**: Load testing, memory usage, response times
5. **Data Integrity**: Foreign keys, constraints, consistency

## Continuous Integration

### GitHub Actions Integration

Tests are configured to run automatically on:
- Pull requests
- Push to main branch
- Scheduled runs

### Test Environment

- **Database**: PostgreSQL with test schema
- **Node.js**: Latest LTS version
- **Dependencies**: Fresh install for each run
- **Isolation**: Each test runs in isolated environment

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure PostgreSQL is running
   - Check DATABASE_URL environment variable
   - Verify database permissions

2. **Test Timeout Errors**
   - Increase Jest timeout in configuration
   - Check for slow database queries
   - Verify test data size

3. **Memory Issues**
   - Reduce test data size
   - Add explicit garbage collection
   - Check for memory leaks in tests

### Debug Mode

Run tests in debug mode for detailed logging:

```bash
npm run test:debug
```

## Best Practices

### Test Writing Guidelines

1. **Descriptive Test Names**: Use clear, descriptive test names
2. **Arrange-Act-Assert**: Follow AAA pattern for test structure
3. **Isolation**: Each test should be independent
4. **Cleanup**: Always clean up test data
5. **Realistic Data**: Use realistic test data
6. **Error Testing**: Test both success and error scenarios

### Performance Testing Guidelines

1. **Baseline Measurements**: Establish performance baselines
2. **Realistic Load**: Use realistic load patterns
3. **Resource Monitoring**: Monitor CPU, memory, and I/O
4. **Regression Detection**: Detect performance regressions
5. **Scalability Testing**: Test with increasing load

### Data Consistency Guidelines

1. **Regular Verification**: Run consistency checks regularly
2. **Automated Checks**: Automate consistency verification
3. **Alerting**: Set up alerts for consistency failures
4. **Documentation**: Document all consistency rules
5. **Monitoring**: Monitor data quality metrics

## Future Enhancements

### Planned Improvements

1. **Visual Test Reports**: HTML test reports with charts
2. **Performance Dashboards**: Real-time performance monitoring
3. **Automated Performance Regression**: Automatic performance regression detection
4. **Load Testing**: More comprehensive load testing scenarios
5. **Security Testing**: Security-focused test scenarios

### Test Infrastructure Improvements

1. **Parallel Test Execution**: Faster test execution
2. **Test Data Factories**: Reusable test data generation
3. **Mock Services**: Better external service mocking
4. **Test Metrics**: Detailed test execution metrics
5. **Test Documentation**: Auto-generated test documentation 