import React, { useEffect, useRef, useState } from 'react';
import { createChart, CandlestickSeries } from 'lightweight-charts';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function TradingChart({ ticker }) {
  const chartContainerRef = useRef();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!ticker) return;
    setLoading(true);

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { type: 'solid', color: 'transparent' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      crosshair: {
        mode: 1, // Normal mode
      },
      timeScale: {
        borderColor: '#4b5563',
      },
    });

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    fetch(`${API_URL}/api/chart/${ticker}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          candlestickSeries.setData(data);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch chart data", err);
        setLoading(false);
      });

    const handleResize = () => {
      chart.applyOptions({ width: chartContainerRef.current.clientWidth });
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [ticker]);

  return (
    <div className="glass-card" style={{ padding: '1rem', position: 'relative' }}>
      <h2>{ticker} Price Chart (1Y)</h2>
      {loading && <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: 'white' }}>Loading chart...</div>}
      <div ref={chartContainerRef} style={{ width: '100%', height: '400px', marginTop: '1rem' }} />
    </div>
  );
}
