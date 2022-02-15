module.exports = {
  preset: '@vue/cli-plugin-unit-jest',
  setupFiles: ['<rootDir>/src/testUtils/setupTests.js'],
  moduleNameMapper: {
    // eslint-disable-next-line vue/max-len
    '\\.(jpg|ico|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/src/testUtils/fileMock.js',
    '\\.(css|less)$': '<rootDir>/src/testUtils/styleMock.js'
  },
  collectCoverageFrom: [
    '<rootDir>/src/**/*.vue'
    // todo in future, if we need to test js files too
    // 'src/**/*.{js,vue}',
    // '!src/main.js', // No need to cover bootstrap file
  ],
  coverageThreshold: {
    global: {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100
    }
  }
}
