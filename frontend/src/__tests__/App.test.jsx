
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../App';

describe('App Component', () => {
  beforeEach(() => {
    // Mock de fetch pour éviter les erreurs
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({
        conversion_rates: {
          USD: 1,
          EUR: 0.85,
          MAD: 10.0
        }
      })
    });
  });

  it('renders without crashing', () => {
    render(<App />);
    expect(document.querySelector('.App')).toBeInTheDocument();
  });

  it('renders CurrencyConverter component', async () => {
    render(<App />);
    const heading = await screen.findByText(/Currency Converter/i, {}, { timeout: 2000 });
    expect(heading).toBeInTheDocument();
  });
});
