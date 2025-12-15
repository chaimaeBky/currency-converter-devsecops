import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from '../App';

// Mock the CurrencyConverter component to avoid API calls
vi.mock('../CurrencyConverter', () => ({
  __esModule: true,
  default: () => (
    <div data-testid="currency-converter">
      <h1>Currency Converter</h1>
      <div>Mocked Converter Component</div>
    </div>
  )
}));

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByTestId('currency-converter')).toBeInTheDocument();
  });

  it('renders CurrencyConverter component', () => {
    render(<App />);
    expect(screen.getByText(/Currency Converter/i)).toBeInTheDocument();
    expect(screen.getByTestId('currency-converter')).toBeInTheDocument();
  });
});