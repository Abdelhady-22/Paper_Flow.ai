import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      background: 'var(--current-card-bg)',
      borderTop: '1px solid var(--current-border)',
      padding: '48px 40px 24px',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 40, marginBottom: 40 }}>
          {/* Brand */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
              <div style={{
                width: 32, height: 32, borderRadius: 8,
                background: 'linear-gradient(135deg, #00D4FF, #00A8CC)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <FileText size={16} color="#fff" />
              </div>
              <span style={{ fontWeight: 700, fontSize: 16 }} className="gradient-text">Paper Flow AI</span>
            </div>
            <p style={{ color: 'var(--current-text-secondary)', fontSize: 13, lineHeight: 1.6 }}>
              AI-Powered Research Paper Assistant for academic analysis and discovery.
            </p>
          </div>

          {/* Features */}
          <div>
            <h4 style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16, color: 'var(--current-text-secondary)' }}>Features</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { to: '/chat', label: 'AI Chatbot' },
                { to: '/summarize', label: 'Summarization' },
                { to: '/translate', label: 'Translation' },
                { to: '/research', label: 'Research Assistant' },
              ].map(l => (
                <li key={l.to}>
                  <Link to={l.to} style={{ color: 'var(--current-text-secondary)', textDecoration: 'none', fontSize: 14, transition: 'color 0.2s' }}
                    onMouseEnter={e => (e.target as HTMLElement).style.color = 'var(--color-primary-cyan)'}
                    onMouseLeave={e => (e.target as HTMLElement).style.color = 'var(--current-text-secondary)'}
                  >{l.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Tools */}
          <div>
            <h4 style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16, color: 'var(--current-text-secondary)' }}>Tools</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                { to: '/ocr', label: 'OCR Scanner' },
                { to: '/qa-generator', label: 'Q&A Generator' },
                { to: '/discover', label: 'Paper Discovery' },
              ].map(l => (
                <li key={l.to}>
                  <Link to={l.to} style={{ color: 'var(--current-text-secondary)', textDecoration: 'none', fontSize: 14, transition: 'color 0.2s' }}
                    onMouseEnter={e => (e.target as HTMLElement).style.color = 'var(--color-primary-cyan)'}
                    onMouseLeave={e => (e.target as HTMLElement).style.color = 'var(--current-text-secondary)'}
                  >{l.label}</Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Info */}
          <div>
            <h4 style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 16, color: 'var(--current-text-secondary)' }}>Info</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
              <li><span style={{ color: 'var(--current-text-secondary)', fontSize: 14 }}>Built with FastAPI & React</span></li>
              <li><span style={{ color: 'var(--current-text-secondary)', fontSize: 14, opacity: 0.6 }}>v1.0.0</span></li>
            </ul>
          </div>
        </div>

        {/* Disclaimer */}
        <div style={{
          display: 'flex', alignItems: 'flex-start', gap: 12, padding: 16,
          background: 'rgba(245, 158, 11, 0.08)', border: '1px solid rgba(245, 158, 11, 0.2)',
          borderRadius: 12, marginBottom: 24,
        }}>
          <span>⚠️</span>
          <p style={{ color: 'var(--current-text-secondary)', fontSize: 13, lineHeight: 1.5, margin: 0 }}>
            <strong>Disclaimer: </strong>
            Paper Flow AI is an academic research tool. Always verify AI-generated content with original sources.
          </p>
        </div>

        {/* Copyright */}
        <div style={{ textAlign: 'center', color: 'var(--current-text-secondary)', fontSize: 13, opacity: 0.6 }}>
          © {new Date().getFullYear()} Paper Flow AI. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
