import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function ExplainablePanel({ signalData }) {
  const [buying, setBuying] = useState(false);
  const [buyQuantity, setBuyQuantity] = useState(10);
  const [currentPrice, setCurrentPrice] = useState(null);

  useEffect(() => {
    if (signalData && signalData.ticker) {
      setCurrentPrice(null);
      fetch(`${API_URL}/api/quote/${signalData.ticker}`)
        .then(res => res.json())
        .then(data => {
          if (data.price) setCurrentPrice(data.price);
        })
        .catch(err => console.error(err));
    }
  }, [signalData]);

  if (!signalData) {
    return (
      <div className="glass-card">
        <h2>Why This Signal?</h2>
        <p className="text-muted">Select a signal to see the AI reasoning.</p>
      </div>
    );
  }

  const { ticker, signal, score, reasons, warnings, tech_details } = signalData;

  const handleBuy = async () => {
    setBuying(true);
    try {
      const res = await fetch(`${API_URL}/api/portfolio/buy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, shares: Number(buyQuantity) })
      });
      const data = await res.json();
      if (data.error) {
        alert(data.error);
      } else {
        alert(data.message);
      }
    } catch (err) {
      alert("Error buying shares");
    } finally {
      setBuying(false);
    }
  };

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2>Why This Signal?</h2>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontWeight: 600 }}>{ticker}</span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              {currentPrice ? `₹${currentPrice.toFixed(2)}` : 'Loading price...'}
            </span>
          </div>
          <span className={`badge badge-${signal.toLowerCase()}`}>{signal} ({score})</span>
          <div style={{ display: 'flex', alignItems: 'center', marginLeft: '0.5rem', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', padding: '0.1rem 0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: '0.5rem' }}>Qty:</span>
            <input 
              type="number" 
              min="1"
              value={buyQuantity} 
              onChange={(e) => setBuyQuantity(e.target.value)}
              style={{ width: '60px', background: 'transparent', border: 'none', color: 'white', outline: 'none' }}
            />
          </div>
          <button 
            onClick={handleBuy}
            disabled={buying}
            style={{
              background: 'var(--success)', color: 'white', border: 'none', 
              padding: '0.25rem 0.75rem', borderRadius: '4px', cursor: buying ? 'not-allowed' : 'pointer', 
              fontWeight: 'bold', marginLeft: '0.5rem'
            }}
          >
            {buying ? '...' : 'Buy Shares'}
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
        <div>
          <h3 className="text-success" style={{ marginBottom: '0.5rem', fontSize: '1rem' }}>Positive Factors</h3>
          {reasons && reasons.length > 0 ? (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {reasons.map((r, idx) => (
                <li key={idx} style={{ marginBottom: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                  <span className="text-success">✓</span> <span>{r}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted">No major positive factors identified.</p>
          )}
        </div>
        
        <div>
          <h3 className="text-danger" style={{ marginBottom: '0.5rem', fontSize: '1rem' }}>Warnings & Risks</h3>
          {warnings && warnings.length > 0 ? (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {warnings.map((w, idx) => (
                <li key={idx} style={{ marginBottom: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                  <span className="text-warning">⚠</span> <span>{w}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted">No major warnings identified.</p>
          )}
        </div>
      </div>
      
      {tech_details && Object.keys(tech_details).length > 0 && (
        <div style={{ marginTop: '1rem', borderTop: '1px solid var(--border)', paddingTop: '1rem' }}>
          <h3 style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Technical Breakdown</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
            {Object.entries(tech_details).map(([key, val]) => (
              <div key={key} style={{ fontSize: '0.75rem', background: 'rgba(255,255,255,0.05)', padding: '0.25rem 0.5rem', borderRadius: '0.25rem' }}>
                <span className="text-muted">{key.replace('_score', '').toUpperCase()}:</span> {typeof val === 'number' ? val.toFixed(2) : val}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
