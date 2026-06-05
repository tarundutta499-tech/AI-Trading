import React, { useState, useEffect } from 'react';

const API_URL = 'http://127.0.0.1:8000';

export default function Portfolio() {
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sellQuantities, setSellQuantities] = useState({});

  const fetchPortfolio = async () => {
    try {
      const res = await fetch(`${API_URL}/api/portfolio`);
      if (!res.ok) throw new Error("Failed to fetch portfolio data");
      const data = await res.json();
      setPortfolio(data);
    } catch (err) {
      setError('Could not load portfolio.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleSell = async (ticker, maxShares) => {
    const qtyToSell = sellQuantities[ticker] ? Number(sellQuantities[ticker]) : maxShares;
    
    if (qtyToSell <= 0 || qtyToSell > maxShares) {
      alert("Invalid quantity to sell.");
      return;
    }

    try {
      const res = await fetch(`${API_URL}/api/portfolio/sell`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, shares: qtyToSell })
      });
      const data = await res.json();
      if (data.error) {
        alert(data.error);
      } else {
        alert(data.message);
        fetchPortfolio(); // Refresh
      }
    } catch (err) {
      alert("Error selling shares");
    }
  };

  if (loading) return <div style={{ padding: '2rem', textAlign: 'center' }}>Loading Paper Trading Simulator...</div>;
  if (error) return <div style={{ padding: '2rem', color: 'var(--danger)' }}>{error}</div>;
  if (!portfolio) return null;

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="glass-card text-center" style={{ padding: '2rem' }}>
          <h3 className="text-muted" style={{ marginBottom: '0.5rem' }}>Available Cash</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)' }}>
            ₹{portfolio.cash_balance.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </div>
        </div>
        <div className="glass-card text-center" style={{ padding: '2rem' }}>
          <h3 className="text-muted" style={{ marginBottom: '0.5rem' }}>Total Equity</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
            ₹{portfolio.total_equity.toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </div>
        </div>
        <div className="glass-card text-center" style={{ padding: '2rem' }}>
          <h3 className="text-muted" style={{ marginBottom: '0.5rem' }}>Unrealized PnL</h3>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: portfolio.unrealized_pnl >= 0 ? 'var(--success)' : 'var(--danger)' }}>
            {portfolio.unrealized_pnl >= 0 ? '+' : '-'}₹{Math.abs(portfolio.unrealized_pnl).toLocaleString(undefined, { maximumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      <div className="glass-card">
        <h2 style={{ marginBottom: '1.5rem' }}>Open Positions</h2>
        {portfolio.positions.length === 0 ? (
          <p className="text-muted">No open positions. Use the Dashboard to find signals and buy shares.</p>
        ) : (
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '1rem' }}>Ticker</th>
                <th style={{ padding: '1rem' }}>Shares</th>
                <th style={{ padding: '1rem' }}>Avg Cost</th>
                <th style={{ padding: '1rem' }}>Current Price</th>
                <th style={{ padding: '1rem' }}>PnL</th>
                <th style={{ padding: '1rem', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.positions.map((p) => {
                const pnl = (p.current_price - p.entry_price) * p.shares;
                const pnlPct = ((p.current_price - p.entry_price) / p.entry_price) * 100;
                const isProfit = pnl >= 0;
                
                return (
                  <tr key={p.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold', color: 'var(--primary)' }}>{p.ticker}</td>
                    <td style={{ padding: '1rem' }}>{p.shares}</td>
                    <td style={{ padding: '1rem' }}>₹{p.entry_price.toFixed(2)}</td>
                    <td style={{ padding: '1rem' }}>₹{p.current_price.toFixed(2)}</td>
                    <td style={{ padding: '1rem', color: isProfit ? 'var(--success)' : 'var(--danger)', fontWeight: 'bold' }}>
                      {isProfit ? '+' : ''}₹{pnl.toFixed(2)} ({pnlPct.toFixed(2)}%)
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', alignItems: 'center' }}>
                        <input 
                          type="number"
                          min="1"
                          max={p.shares}
                          value={sellQuantities[p.ticker] !== undefined ? sellQuantities[p.ticker] : p.shares}
                          onChange={(e) => setSellQuantities({...sellQuantities, [p.ticker]: e.target.value})}
                          style={{ width: '60px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)', color: 'white', padding: '0.25rem', borderRadius: '4px' }}
                        />
                        <button 
                          onClick={() => handleSell(p.ticker, p.shares)}
                          style={{
                            background: 'var(--danger)', color: 'white', border: 'none', 
                            padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold'
                          }}
                        >
                          Sell
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
