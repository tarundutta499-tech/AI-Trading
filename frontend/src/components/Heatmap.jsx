import React from 'react';

export default function Heatmap({ heatmapData, onSelectTicker }) {
  if (!heatmapData || heatmapData.length === 0) {
    return null;
  }

  // Sort by composite score to put strongest signals first (largest blocks)
  const sortedData = [...heatmapData].sort((a, b) => {
    // Sort logic: put high conviction (both high and low scores) first for layout
    const aConviction = Math.abs(50 - a.score);
    const bConviction = Math.abs(50 - b.score);
    return bConviction - aConviction;
  });

  return (
    <div className="glass-card" style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '2.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <h2 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Market Sentiment Heatmap</h2>
            <p className="text-muted" style={{ fontSize: '1rem', maxWidth: '800px', lineHeight: '1.6' }}>
              <strong>What this means:</strong> This heatmap visualizes real-time news sentiment for the NIFTY 50 universe based on Google News headlines from the last 48 hours. 
              The <strong>Color</strong> represents the Sentiment Score (Green = Positive, Slate = Neutral, Red = Negative). 
              The <strong>Size</strong> of the block represents the AI's overall conviction (Composite Score) — larger blocks indicate a strong BUY or strong SELL signal.
            </p>
            <p className="text-muted" style={{ fontSize: '1rem', maxWidth: '800px', lineHeight: '1.6', marginTop: '0.5rem' }}>
              <strong>Purpose:</strong> It provides a macro-level view of market mood at a single glance. It allows quantitative traders to quickly spot overarching trends, identify stocks facing sudden negative press, or discover positive breakout narratives without having to manually read hundreds of articles.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', fontSize: '0.875rem', fontWeight: 600 }}>
            <span style={{ padding: '0.35rem 0.75rem', background: 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)', borderRadius: '4px', color: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>Negative</span>
            <span style={{ padding: '0.35rem 0.75rem', background: 'linear-gradient(135deg, #475569 0%, #334155 100%)', borderRadius: '4px', color: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>Neutral</span>
            <span style={{ padding: '0.35rem 0.75rem', background: 'linear-gradient(135deg, #10b981 0%, #047857 100%)', borderRadius: '4px', color: 'white', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}>Positive</span>
          </div>
        </div>
      </div>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fill, minmax(130px, 1fr))', 
        gap: '0.75rem',
        gridAutoRows: 'minmax(110px, auto)',
        gridAutoFlow: 'dense'
      }}>
        {sortedData.map((data, idx) => {
          let bg = 'linear-gradient(135deg, #475569 0%, #334155 100%)'; // Sleek slate for neutral
          
          if (data.sentiment >= 65) {
            bg = 'linear-gradient(135deg, #10b981 0%, #047857 100%)';
          } else if (data.sentiment > 50) {
            bg = 'linear-gradient(135deg, #34d399 0%, #059669 100%)';
          } else if (data.sentiment <= 35) {
            bg = 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)';
          } else if (data.sentiment < 50) {
            bg = 'linear-gradient(135deg, #f87171 0%, #dc2626 100%)';
          }

          // Dynamic grid sizing based on Composite Score conviction
          const isLarge = data.score >= 65 || data.score <= 35;
          const gridStyle = isLarge ? { gridColumn: 'span 2', gridRow: 'span 2' } : {};

          return (
            <div 
              key={idx} 
              style={{
                ...gridStyle,
                background: bg,
                color: 'white',
                padding: isLarge ? '1.5rem' : '1rem',
                borderRadius: '12px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                cursor: 'pointer',
                border: '1px solid rgba(255,255,255,0.1)',
                position: 'relative',
                overflow: 'hidden'
              }}
              onClick={() => {
                if (onSelectTicker) onSelectTicker(data.ticker);
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.03) translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)';
                e.currentTarget.style.zIndex = 10;
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.3)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1) translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1)';
                e.currentTarget.style.zIndex = 1;
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.1)';
              }}
              title={`Composite Score: ${data.score.toFixed(1)} | Sentiment: ${data.sentiment.toFixed(1)}`}
            >
              <div style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                background: 'linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%)',
                pointerEvents: 'none'
              }} />
              
              <span style={{ 
                fontWeight: 800, 
                fontSize: isLarge ? '1.5rem' : '1.125rem', 
                letterSpacing: '0.05em',
                marginBottom: '0.25rem',
                textShadow: '0 2px 4px rgba(0,0,0,0.5)',
                zIndex: 2
              }}>
                {data.ticker.replace('.NS', '')}
              </span>
              <span style={{ 
                fontSize: isLarge ? '3rem' : '1.75rem', 
                fontWeight: 300,
                textShadow: '0 2px 4px rgba(0,0,0,0.5)',
                zIndex: 2,
                lineHeight: 1
              }}>
                {data.sentiment.toFixed(0)}
              </span>
              {isLarge && (
                <span style={{ 
                  fontSize: '0.875rem', 
                  marginTop: '0.75rem', 
                  opacity: 0.9,
                  background: 'rgba(0,0,0,0.2)',
                  padding: '0.25rem 0.75rem',
                  borderRadius: '999px',
                  fontWeight: 500,
                  zIndex: 2
                }}>
                  Score: {data.score.toFixed(0)}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
