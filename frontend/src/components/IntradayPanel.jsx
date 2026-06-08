import React, { useState, useEffect, useRef } from 'react';
import { createChart, CandlestickSeries } from 'lightweight-charts';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function IntradayPanel() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicker, setSelectedTicker] = useState('^NSEI');
  const [customTicker, setCustomTicker] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  
  const chartContainerRef = useRef();
  const chartRef = useRef(null);
  const seriesRef = useRef(null);

  const fetchSignals = async () => {
    try {
      const res = await fetch(`${API_URL}/api/intraday/signals`);
      const data = await res.json();
      setSignals(data);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const analyzeCustomTicker = async () => {
    if (!customTicker) return;
    setAnalyzing(true);
    try {
      const res = await fetch(`${API_URL}/api/intraday/analyze/${customTicker.toUpperCase()}`);
      const data = await res.json();
      if (!data.error) {
        // Add or update the list
        setSignals(prev => {
          const filtered = prev.filter(s => s.ticker !== data.ticker);
          return [data, ...filtered];
        });
        setSelectedTicker(data.ticker);
        setCustomTicker('');
      } else {
        alert(data.error);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to analyze ticker");
    } finally {
      setAnalyzing(false);
    }
  };

  const loadChart = async (ticker) => {
    if (!chartContainerRef.current) return;
    
    if (!chartRef.current) {
      chartRef.current = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 400,
        layout: {
          background: { color: 'transparent' },
          textColor: '#rgba(255, 255, 255, 0.9)',
        },
        grid: {
          vertLines: { color: 'rgba(255, 255, 255, 0.1)' },
          horzLines: { color: 'rgba(255, 255, 255, 0.1)' },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        }
      });
      seriesRef.current = chartRef.current.addSeries(CandlestickSeries, {
        upColor: '#26a69a', downColor: '#ef5350', borderVisible: false,
        wickUpColor: '#26a69a', wickDownColor: '#ef5350',
      });
    }

    try {
      const res = await fetch(`${API_URL}/api/intraday/chart/${ticker}`);
      const data = await res.json();
      if (!data.error && data.length > 0) {
        if (seriesRef.current) {
          seriesRef.current.setData(data);
        }
      }
    } catch (err) {
      console.error("Failed to load chart", err);
    }
  };

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadChart(selectedTicker);
    return () => {
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
        seriesRef.current = null;
      }
    };
  }, [selectedTicker]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="glass-card" style={{ padding: '2rem' }}>
        <h2>High-Frequency Intraday & F&O Engine</h2>
        <p className="text-muted">Live 5-minute algorithmic scalping for Indices and Commodities.</p>
        
        <div style={{ marginTop: '1rem' }} ref={chartContainerRef} />
      </div>

      <div className="glass-card" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 style={{ margin: 0 }}>Live Intraday Signals</h3>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="text" 
              placeholder="Add Ticker (e.g., TCS.NS)" 
              value={customTicker}
              onChange={(e) => setCustomTicker(e.target.value)}
              style={{ padding: '0.5rem', background: 'rgba(255,255,255,0.05)', color: 'white', border: '1px solid var(--border)', borderRadius: '4px' }}
            />
            <button className="btn" onClick={analyzeCustomTicker} disabled={analyzing}>
              {analyzing ? 'Analyzing...' : 'Add & Analyze'}
            </button>
          </div>
        </div>

        {loading ? <p>Loading real-time feeds...</p> : (
          <div style={{ overflowX: 'auto', marginTop: '1rem' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left' }}>
                  <th style={{ padding: '0.5rem' }}>Ticker</th>
                  <th style={{ padding: '0.5rem' }}>Signal</th>
                  <th style={{ padding: '0.5rem' }}>Price</th>
                  <th style={{ padding: '0.5rem' }}>VWAP</th>
                  <th style={{ padding: '0.5rem' }}>RSI (5m)</th>
                  <th style={{ padding: '0.5rem' }}>MACD</th>
                  <th style={{ padding: '0.5rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {signals.map(s => (
                  <tr key={s.ticker} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '0.5rem', fontWeight: 'bold' }}>{s.ticker.replace('^', '')}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <span style={{
                        padding: '0.2rem 0.5rem', borderRadius: '4px',
                        background: s.signal === 'BUY' ? 'rgba(40,167,69,0.2)' : s.signal === 'SELL' ? 'rgba(220,53,69,0.2)' : 'rgba(255,255,255,0.1)',
                        color: s.signal === 'BUY' ? '#28a745' : s.signal === 'SELL' ? '#dc3545' : 'white'
                      }}>
                        {s.signal} ({s.score})
                      </span>
                    </td>
                    <td style={{ padding: '0.5rem' }}>{s.current_price ? `₹${s.current_price.toFixed(2)}` : '-'}</td>
                    <td style={{ padding: '0.5rem' }}>{s.vwap ? s.vwap.toFixed(2) : '-'}</td>
                    <td style={{ padding: '0.5rem' }}>{s.rsi_5m ? s.rsi_5m.toFixed(1) : '-'}</td>
                    <td style={{ padding: '0.5rem' }}>{s.macd_histogram ? s.macd_histogram.toFixed(2) : '-'}</td>
                    <td style={{ padding: '0.5rem' }}>
                      <button className="btn" style={{ padding: '0.3rem 0.8rem', fontSize: '0.9em' }} onClick={() => setSelectedTicker(s.ticker)}>
                        View Chart
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
