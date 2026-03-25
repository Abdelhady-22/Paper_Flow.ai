import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { Languages, ArrowLeft, Loader, Download, Copy, ArrowLeftRight } from 'lucide-react';

export default function TranslatePage() {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [direction, setDirection] = useState<'en-ar' | 'ar-en'>('en-ar');

  const handleTranslate = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setResult('');
    try {
      const res = await api.post('/translate/', { text: inputText, direction });
      setResult(res.data.translated_text || res.data.translation || res.data.result || JSON.stringify(res.data));
    } catch {
      setResult('Backend is unavailable. Please ensure the gateway is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <PageTransition>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 40px 40px' }}>
          <div className="tool-header">
            <button className="btn-ghost" onClick={() => navigate('/research')}>
              <ArrowLeft size={16} /> Back
            </button>
            <div>
              <h1 style={{ display: 'flex', alignItems: 'center', gap: 12 }} className="gradient-text">
                <Languages size={28} /> Text Translator
              </h1>
              <p className="header-subtitle">Translate research texts between English and Arabic</p>
            </div>
          </div>

          {/* Direction Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, justifyContent: 'center', marginBottom: 32, marginTop: 24 }}>
            <span style={{
              padding: '8px 20px', borderRadius: 100, fontSize: 14, fontWeight: 600,
              background: direction === 'en-ar' ? 'var(--color-primary-cyan)' : 'rgba(255,255,255,0.1)',
              color: direction === 'en-ar' ? '#fff' : 'var(--current-text-secondary)',
              cursor: 'pointer',
            }} onClick={() => setDirection('en-ar')}>English</span>
            <button className="btn-ghost" style={{ padding: 8 }} onClick={() => setDirection(d => d === 'en-ar' ? 'ar-en' : 'en-ar')}>
              <ArrowLeftRight size={18} />
            </button>
            <span style={{
              padding: '8px 20px', borderRadius: 100, fontSize: 14, fontWeight: 600,
              background: direction === 'ar-en' ? 'var(--color-primary-cyan)' : 'rgba(255,255,255,0.1)',
              color: direction === 'ar-en' ? '#fff' : 'var(--current-text-secondary)',
              cursor: 'pointer',
            }} onClick={() => setDirection('ar-en')}>العربية</span>
          </div>

          <div className="tool-content-grid">
            <motion.div className="tool-input-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="card-header">
                <h3>{direction === 'en-ar' ? 'English Text' : 'النص العربي'}</h3>
              </div>
              <textarea className="tool-textarea" placeholder={direction === 'en-ar' ? 'Enter English text...' : 'أدخل النص العربي...'}
                value={inputText} onChange={e => setInputText(e.target.value)} rows={10}
                dir={direction === 'ar-en' ? 'rtl' : 'ltr'}
              />
              <button className="btn-process" onClick={handleTranslate} disabled={loading || !inputText.trim()}>
                {loading ? <><Loader size={18} className="spin" /> Translating...</> : 'Translate'}
              </button>
            </motion.div>

            <motion.div className="tool-output-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <div className="card-header">
                <h3>{direction === 'en-ar' ? 'الترجمة العربية' : 'English Translation'}</h3>
                {result && (
                  <button className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: 13 }}
                    onClick={() => navigator.clipboard.writeText(result)}
                  ><Copy size={14} /> Copy</button>
                )}
              </div>
              {!result && !loading && (
                <div className="empty-output">
                  <Languages size={48} />
                  <p>Translation will appear here</p>
                </div>
              )}
              {loading && (
                <div className="loading-output">
                  <Loader size={40} className="spin" />
                  <p>Translating your text...</p>
                </div>
              )}
              {result && (
                <div style={{
                  padding: 24, background: 'rgba(255,255,255,0.02)', borderRadius: 12,
                  border: '1px solid var(--current-border)', lineHeight: 1.8,
                  direction: direction === 'en-ar' ? 'rtl' : 'ltr',
                  fontFamily: direction === 'en-ar' ? 'var(--font-arabic)' : 'var(--font-primary)',
                  fontSize: 16,
                }}>
                  {result}
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </PageTransition>
    </>
  );
}
