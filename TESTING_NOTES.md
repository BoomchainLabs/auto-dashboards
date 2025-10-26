Testing framework: Jest
These tests validate the presence and structure of jest.config.js. If the file is not present (e.g., in this PR or in certain build contexts), the suite is skipped gracefully.