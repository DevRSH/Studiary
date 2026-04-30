/**
 * Jest test setup — global mocks and testing library configuration.
 */

import '@testing-library/jest-dom';

// Mock de localStorage para tests
const localStorageMock: Storage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};

Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock de virtual:pwa-register (Vite PWA no disponible en Jest)
jest.mock('virtual:pwa-register', () => ({
  registerSW: jest.fn(),
}));
