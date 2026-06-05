import React, { useState, useEffect } from 'react';
import TopSignals from './components/TopSignals';
import Portfolio from './components/Portfolio';
import Heatmap from './components/Heatmap';
import NewsFeed from './components/NewsFeed';
import ExplainablePanel from './components/ExplainablePanel';
import Meters from './components/Meters';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [data, setData] = useState({ top_signals: [], all_signals: [], positions: [], heatmap: [], news: [] });
  const [loading, setLoading] = useState(true);
  const [forceRunStatus, setForceRunStatus] = useState('');
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API_URL}/api/dashboard`);
      const json = await res.json();
      setData(json);
      if (json.top_signals.length > 0 && !selectedSignal) {
        setSelectedSignal(json.top_signals[0]);
      }
      setLoading(false);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const handleForceRun = async () => {
    setForceRunStatus('Starting analysis...');
    try {
      await fetch(`${API_URL}/api/force-run`, { method: 'POST' });
      setForceRunStatus('Analysis running in background. Data will refresh soon.');
      setTimeout(() => fetchDashboard(), 5000); // Check again in 5 seconds
    } catch (err) {
      setForceRunStatus('Failed to start analysis.');
    }
  };

  return (
    <div className="app-container">
      <header>
        <div>
          <h1>AI Trading Agent</h1>
          <p className="text-muted">Indian Equity Markets (NSE) • Indicative Signals Only</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span className="text-muted">{forceRunStatus}</span>
          <button className="btn" onClick={handleForceRun}>Force Run Analysis</button>
        </div>
      </header>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
        <button 
          className={`btn ${activeTab === 'dashboard' ? '' : 'btn-secondary'}`} 
          style={{ background: activeTab === 'dashboard' ? 'var(--primary)' : 'transparent', border: activeTab === 'dashboard' ? 'none' : '1px solid var(--border)', color: activeTab === 'dashboard' ? 'white' : 'var(--text-muted)' }}
          onClick={() => setActiveTab('dashboard')}
        >
          Dashboard
        </button>
        <button 
          className={`btn ${activeTab === 'portfolio' ? '' : 'btn-secondary'}`} 
          style={{ background: activeTab === 'portfolio' ? 'var(--primary)' : 'transparent', border: activeTab === 'portfolio' ? 'none' : '1px solid var(--border)', color: activeTab === 'portfolio' ? 'white' : 'var(--text-muted)' }}
          onClick={() => setActiveTab('portfolio')}
        >
          Paper Trading
        </button>
        <button 
          className={`btn ${activeTab === 'news' ? '' : 'btn-secondary'}`} 
          style={{ background: activeTab === 'news' ? 'var(--primary)' : 'transparent', border: activeTab === 'news' ? 'none' : '1px solid var(--border)', color: activeTab === 'news' ? 'white' : 'var(--text-muted)' }}
          onClick={() => setActiveTab('news')}
        >
          News Updates
        </button>
        <button 
          className={`btn ${activeTab === 'heatmap' ? '' : 'btn-secondary'}`} 
          style={{ background: activeTab === 'heatmap' ? 'var(--primary)' : 'transparent', border: activeTab === 'heatmap' ? 'none' : '1px solid var(--border)', color: activeTab === 'heatmap' ? 'white' : 'var(--text-muted)' }}
          onClick={() => setActiveTab('heatmap')}
        >
          Market Heatmap
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>Loading dashboard...</div>
      ) : (
        <>
          {activeTab === 'dashboard' ? (
            <>
              <div className="grid-dashboard">
                <TopSignals signals={data.all_signals} onSelectSignal={setSelectedSignal} selectedTicker={selectedSignal?.ticker} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                  <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem' }}>
                    <h3 style={{ margin: 0, fontSize: '1rem' }}>Quick Select Top Stocks:</h3>
                    <select 
                      style={{ padding: '0.5rem', background: 'var(--bg-card)', color: 'white', border: '1px solid var(--border)', borderRadius: '4px', outline: 'none', cursor: 'pointer' }}
                      value={selectedSignal?.ticker || ''}
                      onChange={(e) => {
                        const signal = data.all_signals.find(s => s.ticker === e.target.value);
                        if (signal) setSelectedSignal(signal);
                      }}
                    >
                      {data.top_signals.map(s => (
                        <option key={s.ticker} value={s.ticker}>
                          {s.ticker} (Score: {s.score})
                        </option>
                      ))}
                    </select>
                  </div>
                  <Meters signalData={selectedSignal} />
                  <ExplainablePanel signalData={selectedSignal} />
                  <div className="glass-card">
                    <h2>System Status</h2>
                    <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span className="text-muted">Market Hours</span>
                        <span className="text-success">OPEN</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span className="text-muted">Database</span>
                        <span className="text-success">CONNECTED</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span className="text-muted">AI Engine</span>
                        <span className="text-success">ONLINE</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : activeTab === 'portfolio' ? (
            <div className="grid-full">
              <Portfolio positions={data.positions} />
            </div>
          ) : activeTab === 'news' ? (
            <div className="grid-full">
              <NewsFeed newsData={data.news} />
            </div>
          ) : (
            <div className="grid-full">
              <Heatmap 
                heatmapData={data.heatmap} 
                onSelectTicker={(ticker) => {
                  const signal = data.all_signals.find(s => s.ticker === ticker);
                  if (signal) {
                    setSelectedSignal(signal);
                    setActiveTab('dashboard');
                  }
                }} 
              />
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
