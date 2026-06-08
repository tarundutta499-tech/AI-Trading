import React, { useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function BacktestingPanel() {
  const [ticker, setTicker] = useState('RELIANCE.NS');
  const [years, setYears] = useState(1);
  const [trailingStop, setTrailingStop] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState(null);

  const runBacktest = async () => {
    setLoading(true);
    setResults(null);
    try {
      const res = await fetch(`${API_URL}/api/backtest/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          ticker, 
          years, 
          initial_capital: 100000.0,
          trailing_stop_pct: trailingStop ? Number(trailingStop) : null
        })
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
      alert("Failed to run backtest");
    } finally {
      setLoading(false);
    }
  };

  const runOptimization = async () => {
    setOptimizing(true);
    setOptimizationResult(null);
    try {
      const res = await fetch(`${API_URL}/api/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          ticker, 
          years, 
          trailing_stop_pct: trailingStop ? Number(trailingStop) : 10.0 // Default to 10 for optimize if not set
        })
      });
      const data = await res.json();
      setOptimizationResult(data);
    } catch (err) {
      console.error(err);
      alert("Failed to run optimization");
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '2rem' }}>
      <h2>Backtesting Engine</h2>
      <p className="text-muted" style={{ marginBottom: '1rem' }}>Simulate historical trading performance based on our AI signals.</p>
      
      <div style={{ background: 'rgba(255, 193, 7, 0.1)', borderLeft: '4px solid #ffc107', padding: '1rem', marginBottom: '1.5rem', color: '#ffc107' }}>
        <strong>⚠️ Note:</strong> Historical backtests use available historical technical data and may not reflect future performance.
      </div>
      
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <input 
          type="text" 
          value={ticker} 
          onChange={e => setTicker(e.target.value.toUpperCase())}
          placeholder="Ticker Symbol (e.g., RELIANCE.NS)"
          style={{ padding: '0.5rem', background: 'var(--bg-card)', color: 'white', border: '1px solid var(--border)', borderRadius: '4px' }}
        />
        <select 
          value={years} 
          onChange={e => setYears(Number(e.target.value))}
          style={{ padding: '0.5rem', background: 'var(--bg-card)', color: 'white', border: '1px solid var(--border)', borderRadius: '4px' }}
        >
          <option value={1}>1 Year</option>
          <option value={3}>3 Years</option>
          <option value={5}>5 Years</option>
        </select>
        <select 
          value={trailingStop} 
          onChange={e => setTrailingStop(e.target.value)}
          style={{ padding: '0.5rem', background: 'var(--bg-card)', color: 'white', border: '1px solid var(--border)', borderRadius: '4px' }}
        >
          <option value="">No Trailing Stop</option>
          <option value="5">5% Trailing Stop</option>
          <option value="10">10% Trailing Stop</option>
          <option value="15">15% Trailing Stop</option>
          <option value="20">20% Trailing Stop</option>
        </select>
        <button className="btn" onClick={runBacktest} disabled={loading || optimizing}>
          {loading ? 'Running...' : 'Run Backtest'}
        </button>
        <button className="btn btn-secondary" onClick={runOptimization} disabled={loading || optimizing} style={{background: 'linear-gradient(45deg, #6a11cb, #2575fc)', border: 'none'}}>
          {optimizing ? 'Optimizing Grid Search...' : 'Optimize Strategy (AI)'}
        </button>
      </div>

      {loading && <div style={{ textAlign: 'center', padding: '2rem' }}>Crunching numbers... this may take a few seconds.</div>}
      {optimizing && <div style={{ textAlign: 'center', padding: '2rem' }}>Running grid search optimization across 16 parameter combinations. Please wait...</div>}

      {optimizationResult && !optimizationResult.error && (
        <div style={{ background: 'rgba(40, 167, 69, 0.1)', borderLeft: '4px solid #28a745', padding: '1.5rem', marginBottom: '2rem' }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#28a745' }}>Optimization Complete for {optimizationResult.ticker}!</h3>
          <p style={{ margin: 0 }}>
            Best BUY Score Threshold: <strong>{optimizationResult.best_buy_threshold}</strong><br/>
            Best SELL Score Threshold: <strong>{optimizationResult.best_sell_threshold}</strong><br/>
            Optimized Profit Factor: <strong className="text-success">{optimizationResult.best_profit_factor.toFixed(2)}</strong>
          </p>
          <p className="text-muted" style={{ marginTop: '0.5rem', fontSize: '0.9em' }}>
            To see full details, run a standard Backtest. Note: Real-time signals currently use standard thresholds (65/35). In the next update, we will apply optimized thresholds automatically.
          </p>
        </div>
      )}

      {results && results.session && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Strategy Return</h3>
              <h2 className={results.session.total_roi >= 0 ? 'text-success' : 'text-danger'}>
                {results.session.total_roi.toFixed(2)}%
              </h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Benchmark Return</h3>
              <h2 className={results.session.benchmark_return >= 0 ? 'text-success' : 'text-danger'}>
                {results.session.benchmark_return.toFixed(2)}%
              </h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Win Rate</h3>
              <h2>{results.session.win_rate.toFixed(2)}%</h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Max Drawdown</h3>
              <h2 className="text-danger">-{results.session.max_drawdown.toFixed(2)}%</h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Sharpe Ratio</h3>
              <h2>{results.session.sharpe_ratio.toFixed(2)}</h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Profit Factor</h3>
              <h2>{results.session.profit_factor.toFixed(2)}</h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">BUY / SELL Signals</h3>
              <h2>{results.session.buy_signals} / {results.session.sell_signals}</h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Completed Trades</h3>
              <h2>{results.session.completed_trades}</h2>
            </div>
            <div className="glass-card" style={{ padding: '1rem', textAlign: 'center' }}>
              <h3 className="text-muted">Avg Trade Duration</h3>
              <h2>{results.session.avg_trade_duration.toFixed(1)} Days</h2>
            </div>
          </div>
          
          {results.trades && results.trades.length > 0 && (
            <>
              <h3>Trade Log</h3>
              <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left' }}>
                      <th style={{ padding: '0.5rem' }}>Entry Date</th>
                      <th style={{ padding: '0.5rem' }}>Exit Date</th>
                      <th style={{ padding: '0.5rem' }}>Entry Price</th>
                      <th style={{ padding: '0.5rem' }}>Exit Price</th>
                      <th style={{ padding: '0.5rem' }}>PnL (%)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.trades.map(trade => (
                      <tr key={trade.id} style={{ borderBottom: '1px solid var(--border)' }}>
                        <td style={{ padding: '0.5rem' }}>{new Date(trade.entry_date).toLocaleDateString()}</td>
                        <td style={{ padding: '0.5rem' }}>{new Date(trade.exit_date).toLocaleDateString()}</td>
                        <td style={{ padding: '0.5rem' }}>₹{trade.entry_price.toFixed(2)}</td>
                        <td style={{ padding: '0.5rem' }}>₹{trade.exit_price.toFixed(2)}</td>
                        <td style={{ padding: '0.5rem' }} className={trade.pnl_percent >= 0 ? 'text-success' : 'text-danger'}>
                          {trade.pnl_percent.toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
