import '@testing-library/jest-dom';
import { vi, beforeAll, afterEach, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';

// Mock fetch globally
beforeAll(() => {
  global.fetch = vi.fn();
});

// Cleanup after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Restore all mocks after tests
afterAll(() => {
  vi.restoreAllMocks();
});