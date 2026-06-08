import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function ScreenerPanel() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScreenerResults();
  }, []);

  const fetchScreenerResults = async () => {
    try {
      const res = await fetch(`${API_URL}/api/screener/results`);
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '2rem' }}>
      <h2>The Golden Screener</h2>
      <p className="text-muted" style={{ marginBottom: '1.5rem' }}>
        Automated nightly scans of the NIFTY 50. Only stocks that beat the benchmark and maintain a Profit Factor &gt; 1.5 over a 3-year backtest are listed here.
      </p>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>Loading screener results...</div>
      ) : results.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#ffc107' }}>
          No stocks passed the Golden Checklist today. The market may be highly volatile or trending poorly.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left' }}>
                <th style={{ padding: '1rem' }}>Ticker</th>
                <th style={{ padding: '1rem' }}>Live Signal</th>
                <th style={{ padding: '1rem' }}>Strategy Return</th>
                <th style={{ padding: '1rem' }}>Benchmark</th>
                <th style={{ padding: '1rem' }}>Profit Factor</th>
                <th style={{ padding: '1rem' }}>Sharpe Ratio</th>
                <th style={{ padding: '1rem' }}>Max Drawdown</th>
              </tr>
            </thead>
            <tbody>
              {results.map(r => (
                <tr key={r.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '1rem', fontWeight: 'bold' }}>{r.ticker}</td>
                  <td style={{ padding: '1rem' }}>
                    <span style={{
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      background: r.live_signal === 'BUY' ? 'rgba(40, 167, 69, 0.2)' : r.live_signal === 'SELL' ? 'rgba(220, 53, 69, 0.2)' : 'rgba(255, 255, 255, 0.1)',
                      color: r.live_signal === 'BUY' ? '#28a745' : r.live_signal === 'SELL' ? '#dc3545' : '#ccc',
                      fontWeight: 'bold'
                    }}>
                      {r.live_signal}
                    </span>
                  </td>
                  <td style={{ padding: '1rem' }} className={r.strategy_return >= 0 ? 'text-success' : 'text-danger'}>
                    {r.strategy_return.toFixed(2)}%
                  </td>
                  <td style={{ padding: '1rem' }} className={r.benchmark_return >= 0 ? 'text-success' : 'text-danger'}>
                    {r.benchmark_return.toFixed(2)}%
                  </td>
                  <td style={{ padding: '1rem' }} className="text-success">{r.profit_factor.toFixed(2)}</td>
                  <td style={{ padding: '1rem' }}>{r.sharpe_ratio.toFixed(2)}</td>
                  <td style={{ padding: '1rem' }} className="text-danger">{(r.max_drawdown || 0).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
