/**
 * Mock for @shared/api/client — replaces Axios with a Jest mock.
 */

import { jest } from '@jest/globals';

export const apiClient = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  patch: jest.fn(),
  delete: jest.fn(),
};
