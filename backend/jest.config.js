export default {
  testEnvironment: 'node',
  extensionsToTreatAsEsm: ['.js'],
  coverageDirectory: 'coverage',
  collectCoverageFrom: ['src/**/*.js'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'], // optional, if needed
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};