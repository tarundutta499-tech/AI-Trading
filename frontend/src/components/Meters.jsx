import React from 'react';

export default function Meters({ signalData }) {
  if (!signalData) return null;

  const { risk_score, confidence_score } = signalData;

  // Risk Score: 0-30 High (Red), 31-70 Medium (Yellow), 71-100 Low (Green)
  // Wait, risk score is inverted. Higher is safer.
  let riskColor = 'var(--danger)';
  let riskLabel = 'High Risk';
  if (risk_score > 70) {
    riskColor = 'var(--success)';
    riskLabel = 'Low Risk';
  } else if (risk_score > 30) {
    riskColor = 'var(--warning)';
    riskLabel = 'Medium Risk';
  }

  // Confidence: 0-100
  let confColor = 'var(--primary)';
  if (confidence_score > 80) confColor = 'var(--success)';
  else if (confidence_score < 50) confColor = 'var(--warning)';

  return (
    <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem' }}>AI Confidence</h3>
          <span style={{ fontWeight: 600, color: confColor }}>{confidence_score}%</span>
        </div>
        <div style={{ width: '100%', background: 'var(--border)', height: '8px', borderRadius: '4px' }}>
          <div style={{ width: `${confidence_score}%`, background: confColor, height: '100%', borderRadius: '4px' }}></div>
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <h3 style={{ fontSize: '1rem' }}>Risk Meter</h3>
          <span style={{ fontWeight: 600, color: riskColor }}>{riskLabel} ({risk_score})</span>
        </div>
        <div style={{ width: '100%', background: 'var(--border)', height: '8px', borderRadius: '4px' }}>
          <div style={{ width: `${risk_score}%`, background: riskColor, height: '100%', borderRadius: '4px' }}></div>
        </div>
        <p className="text-muted" style={{ fontSize: '0.75rem', marginTop: '0.5rem' }}>Higher score = Lower risk</p>
      </div>
    </div>
  );
}
