import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CurrencyConverter from '../CurrencyConverter';

describe('CurrencyConverter Component', () => {
  const mockRatesResponse = {
    status: 'success',
    base: 'USD',
    conversion_rates: {
      USD: 1,
      EUR: 0.85,
      MAD: 10.0,
      GBP: 0.73,
      JPY: 110.0
    },
    time_last_update_utc: 'Mon, 08 Dec 2025 00:00:00 +0000'
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default successful fetch mock
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => mockRatesResponse
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders the component', async () => {
    render(<CurrencyConverter />);
    
    // Check loading state
    expect(screen.getByText(/Loading exchange rates/i)).toBeInTheDocument();
    
    // Wait for content to load
    await waitFor(() => {
      expect(screen.getByText(/Currency Converter/i)).toBeInTheDocument();
    });
  });

  it('displays loading state initially', () => {
    // Make fetch never resolve
    global.fetch.mockImplementation(() => new Promise(() => {}));
    
    render(<CurrencyConverter />);
    expect(screen.getByText(/Loading exchange rates/i)).toBeInTheDocument();
  });

  it('fetches and displays exchange rates', async () => {
    render(<CurrencyConverter />);

    await waitFor(() => {
      const selects = screen.getAllByRole('combobox');
      expect(selects).toHaveLength(2);
    });

    const selects = screen.getAllByRole('combobox');
    expect(selects[0]).toHaveValue('USD');
    expect(selects[1]).toHaveValue('EUR');
  });

  it('converts currency correctly', async () => {
    render(<CurrencyConverter />);

    await waitFor(() => {
      expect(screen.getAllByRole('combobox')).toHaveLength(2);
    });

    const input = screen.getByPlaceholderText(/Enter amount/i);
    
    // Clear input and type 100
    await userEvent.clear(input);
    await userEvent.type(input, '100');

    await waitFor(() => {
      expect(screen.getByText(/100 USD/)).toBeInTheDocument();
      expect(screen.getByText(/85.0000 EUR/)).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('switches currencies when button is clicked', async () => {
    render(<CurrencyConverter />);

    await waitFor(() => {
      expect(screen.getAllByRole('combobox')).toHaveLength(2);
    });

    const switchButton = screen.getByRole('button', { name: /⇄/i });
    await userEvent.click(switchButton);

    await waitFor(() => {
      const selects = screen.getAllByRole('combobox');
      expect(selects[0]).toHaveValue('EUR'); // Switched
      expect(selects[1]).toHaveValue('USD'); // Switched
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock failed API call
    global.fetch.mockRejectedValueOnce(new Error('Network Error'));
    
    render(<CurrencyConverter />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    });
  });

  it('handles HTTP 500 errors', async () => {
    // Mock server error
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ error: 'Server Error' })
    });
    
    render(<CurrencyConverter />);

    await waitFor(() => {
      expect(screen.getByText(/Error:/i)).toBeInTheDocument();
    });
  });
});