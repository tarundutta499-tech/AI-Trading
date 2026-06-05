import React, { useState } from 'react';

export default function TopSignals({ signals, onSelectSignal, selectedTicker }) {
  const [sortConfig, setSortConfig] = useState({ key: 'score', direction: 'desc' });

  if (!signals || signals.length === 0) {
    return (
      <div className="glass-card" style={{ overflowX: 'auto' }}>
        <h2>Market Watchlist (NIFTY 50)</h2>
        <p className="text-muted">No signals available yet. Run analysis to generate signals.</p>
      </div>
    );
  }

  const handleSort = (key) => {
    let direction = 'desc';
    if (sortConfig.key === key && sortConfig.direction === 'desc') {
      direction = 'asc';
    }
    setSortConfig({ key, direction });
  };

  const sortedSignals = [...signals].sort((a, b) => {
    let valA = a[sortConfig.key];
    let valB = b[sortConfig.key];
    
    // Handle nulls
    if (valA === null || valA === undefined) valA = -9999;
    if (valB === null || valB === undefined) valB = -9999;
    
    // Handle strings (like ticker or signal)
    if (typeof valA === 'string' && typeof valB === 'string') {
      return sortConfig.direction === 'asc' 
        ? valA.localeCompare(valB) 
        : valB.localeCompare(valA);
    }
    
    // Handle numbers
    return sortConfig.direction === 'asc' ? valA - valB : valB - valA;
  });

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return ' ↕';
    return sortConfig.direction === 'asc' ? ' ↑' : ' ↓';
  };

  const headerStyle = { padding: '0.75rem 1rem', cursor: 'pointer', userSelect: 'none' };

  return (
    <div className="glass-card" style={{ overflowX: 'auto', overflowY: 'auto', maxHeight: '800px', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ marginBottom: '1rem', flexShrink: 0 }}>Market Watchlist (NIFTY 50)</h2>
      <div style={{ overflowY: 'auto', flexGrow: 1 }}>
        <table style={{ whiteSpace: 'nowrap', width: '100%' }}>
          <thead style={{ position: 'sticky', top: 0, background: 'rgba(15, 23, 42, 0.95)', zIndex: 10 }}>
            <tr>
              <th style={headerStyle} onClick={() => handleSort('ticker')}>Ticker{getSortIcon('ticker')}</th>
              <th style={headerStyle} onClick={() => handleSort('signal')}>Signal{getSortIcon('signal')}</th>
              <th style={headerStyle} onClick={() => handleSort('score')}>Comp{getSortIcon('score')}</th>
              <th style={headerStyle} onClick={() => handleSort('confidence_score')}>Conf %{getSortIcon('confidence_score')}</th>
              <th style={headerStyle} onClick={() => handleSort('technical_score')}>Tech{getSortIcon('technical_score')}</th>
              <th style={headerStyle} onClick={() => handleSort('fundamental_score')}>Fund{getSortIcon('fundamental_score')}</th>
              <th style={headerStyle} onClick={() => handleSort('sentiment_score')}>Sent{getSortIcon('sentiment_score')}</th>
              <th style={headerStyle} onClick={() => handleSort('risk_score')}>Risk{getSortIcon('risk_score')}</th>
              <th style={headerStyle} onClick={() => handleSort('market_score')}>Market{getSortIcon('market_score')}</th>
              <th style={headerStyle} onClick={() => handleSort('sector_score')}>Sector{getSortIcon('sector_score')}</th>
            </tr>
          </thead>
          <tbody>
            {sortedSignals.map((s, idx) => (
              <tr 
                key={idx} 
                onClick={() => onSelectSignal(s)} 
                style={{ cursor: 'pointer', background: selectedTicker === s.ticker ? 'rgba(255,255,255,0.05)' : 'transparent' }}
              >
                <td style={{ fontWeight: 600, color: 'var(--primary)' }}>{s.ticker}</td>
                <td>
                  <span className={`badge badge-${s.signal.toLowerCase()}`}>
                    {s.signal}
                  </span>
                </td>
                <td style={{ fontWeight: 600 }}>{s.score.toFixed(1)}</td>
                <td className="text-success">{s.confidence_score}</td>
                <td className="text-muted">{s.technical_score}</td>
                <td className="text-muted">{s.fundamental_score === null ? 'N/A' : s.fundamental_score}</td>
                <td className="text-muted">{s.sentiment_score}</td>
                <td className="text-muted">{s.risk_score}</td>
                <td className="text-muted">{s.market_score}</td>
                <td className="text-muted">{s.sector_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
