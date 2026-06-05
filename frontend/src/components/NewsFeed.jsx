import React from 'react';

export default function NewsFeed({ newsData }) {
  if (!newsData || newsData.length === 0) {
    return (
      <div className="glass-card">
        <h2>Latest News</h2>
        <p className="text-muted">No recent news available.</p>
      </div>
    );
  }

  return (
    <div className="glass-card">
      <h2 style={{ marginBottom: '1rem' }}>Latest News (Tracked Tickers)</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {newsData.map((item, idx) => {
          let sentColor = 'text-warning';
          if (item.sentiment > 0.1) sentColor = 'text-success';
          else if (item.sentiment < -0.1) sentColor = 'text-danger';

          return (
            <div key={idx} style={{ paddingBottom: '1rem', borderBottom: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                <span className="badge badge-hold" style={{ background: 'var(--bg-dark)' }}>{item.ticker}</span>
                <span className={sentColor} style={{ fontWeight: 600 }}>
                  Sentiment: {item.sentiment > 0 ? '+' : ''}{item.sentiment.toFixed(2)}
                </span>
              </div>
              <a href={item.link} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: 500, display: 'block', marginBottom: '0.25rem' }}>
                {item.title}
              </a>
              <span className="text-muted" style={{ fontSize: '0.75rem' }}>{item.published}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
