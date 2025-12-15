import React, { useState, useEffect } from 'react';
import './converter.css';

const CurrencyConverter = () => {
  const [rates, setRates] = useState({});
  const [amount, setAmount] = useState(1);
  const [fromCurrency, setFromCurrency] = useState('USD');
  const [toCurrency, setToCurrency] = useState('EUR');
  const [convertedAmount, setConvertedAmount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

 // In your CurrencyConverter component
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

useEffect(() => {
  fetch(`${API_URL}/rates`)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      return res.json();
    })
    .then(data => {
      if (data.status === "success") {
        setRates(data.conversion_rates);
      } else {
        throw new Error(data.message || "Failed to fetch rates");
      }
      setLoading(false);
    })
    .catch(err => {
      console.error("Error fetching rates:", err);
      setError(`API Error: ${err.message}. URL: ${API_URL}`);
      setLoading(false);
    });
}, []);

  const Convert = () => {
    if (!rates[fromCurrency] || !rates[toCurrency]) return;
    const result = (amount / rates[fromCurrency]) * rates[toCurrency];
    setConvertedAmount(result);
  };

  useEffect(() => {
    if (Object.keys(rates).length > 0 && amount > 0) {
      Convert();
    }
  }, [amount, fromCurrency, toCurrency, rates]);

  const handleSwitch = () => {
    setFromCurrency(toCurrency);
    setToCurrency(fromCurrency);
  };

  const handleAmountChange = (e) => {
    const value = e.target.value;
    
    // Allow empty string while typing
    if (value === '') {
      setAmount('');
      return;
    }
    
    // Parse the value and ensure it's a valid number
    const parsedValue = parseFloat(value);
    if (!isNaN(parsedValue) && parsedValue >= 0) {
      setAmount(parsedValue);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        Loading exchange rates...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', color: 'red' }}>
        Error: {error}
        <br />
        <small>API URL: {API_URL}</small>
      </div>
    );
  }

  return (
    <div className="converter-container">
      <h1>Currency Converter</h1>

      <input
        type="number"
        value={amount}
        onChange={handleAmountChange}
        placeholder="Enter amount"
        className="converter-input"
        min="0"
        step="any"
      />

      <div className="currency-row">
        <select
          value={fromCurrency}
          onChange={(e) => setFromCurrency(e.target.value)}
          className="currency-select"
        >
          {Object.keys(rates).map(curr => (
            <option key={curr} value={curr}>{curr}</option>
          ))}
        </select>

        <button className="switch-button" onClick={handleSwitch}>⇄</button>

        <select
          value={toCurrency}
          onChange={(e) => setToCurrency(e.target.value)}
          className="currency-select"
        >
          {Object.keys(rates).map(curr => (
            <option key={curr} value={curr}>{curr}</option>
          ))}
        </select>
      </div>

      {convertedAmount !== null && amount > 0 && (
        <div className="converted-result">
          <p>{amount} {fromCurrency} = {convertedAmount.toFixed(4)} {toCurrency}</p>
          <p className="converted-rate">
            Rate: 1 {fromCurrency} = {((1 / rates[fromCurrency]) * rates[toCurrency]).toFixed(6)} {toCurrency}
          </p>
        </div>
      )}

      <div className="timestamp">
        Exchange rates updated: {new Date().toLocaleString()}
      </div>
    </div>
  );
};

export default CurrencyConverter;