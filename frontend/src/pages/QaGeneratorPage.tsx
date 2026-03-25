import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { HelpCircle, ArrowLeft, Loader, Download, ChevronDown, ChevronUp } from 'lucide-react';

interface QA {
  question: string;
  answer: string;
}

export default function QaGeneratorPage() {
  const navigate = useNavigate();
  const [inputText, setInputText] = useState('');
  const [qaList, setQaList] = useState<QA[]>([]);
  const [loading, setLoading] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [count, setCount] = useState(5);

  const handleGenerate = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setQaList([]);
    try {
      const res = await api.post('/qa/generate', { text: inputText, count });
      const data = res.data;
      const pairs = data.qa_pairs || data.questions || data;
      if (Array.isArray(pairs)) {
        setQaList(pairs.map((p: any) => ({ question: p.question || p.q, answer: p.answer || p.a })));
      } else {
        setQaList([{ question: 'Response', answer: JSON.stringify(data) }]);
      }
    } catch {
      setQaList([{ question: 'Error', answer: 'Backend is unavailable. Please ensure the gateway is running on port 8000.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    const content = qaList.map((qa, i) => `Q${i + 1}: ${qa.question}\nA: ${qa.answer}`).join('\n\n');
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'qa-pairs.txt'; a.click();
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
                <HelpCircle size={28} /> Q&A Generator
              </h1>
              <p className="header-subtitle">Auto-generate question-answer pairs for study guides</p>
            </div>
          </div>

          <div className="tool-content-grid">
            <motion.div className="tool-input-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="card-header">
                <h3>Source Text</h3>
              </div>
              <textarea className="tool-textarea" placeholder="Paste your research text here..."
                value={inputText} onChange={e => setInputText(e.target.value)} rows={10}
              />
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 12 }}>
                <label style={{ fontSize: 14, color: 'var(--current-text-secondary)' }}>Questions:</label>
                <select value={count} onChange={e => setCount(Number(e.target.value))} style={{
                  background: 'var(--current-input-bg)', border: '1px solid var(--current-border)',
                  borderRadius: 8, padding: '8px 12px', color: 'var(--current-text-primary)',
                  fontSize: 14, outline: 'none', fontFamily: 'var(--font-primary)',
                }}>
                  {[3, 5, 10, 15].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>
              <button className="btn-process" onClick={handleGenerate} disabled={loading || !inputText.trim()}>
                {loading ? <><Loader size={18} className="spin" /> Generating...</> : 'Generate Q&A'}
              </button>
            </motion.div>

            <motion.div className="tool-output-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <div className="card-header">
                <h3>Generated Q&A</h3>
                {qaList.length > 0 && (
                  <button className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: 13 }} onClick={handleDownload}>
                    <Download size={14} /> Download
                  </button>
                )}
              </div>
              {qaList.length === 0 && !loading && (
                <div className="empty-output">
                  <HelpCircle size={48} />
                  <p>Generated questions will appear here</p>
                </div>
              )}
              {loading && (
                <div className="loading-output">
                  <Loader size={40} className="spin" />
                  <p>Generating questions from your text...</p>
                </div>
              )}
              {qaList.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12, overflowY: 'auto', flex: 1 }}>
                  {qaList.map((qa, i) => (
                    <div key={i} style={{
                      background: 'rgba(255,255,255,0.03)', border: '1px solid var(--current-border)',
                      borderRadius: 12, overflow: 'hidden',
                    }}>
                      <button onClick={() => setExpanded(expanded === i ? null : i)} style={{
                        width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        padding: '16px 20px', background: 'transparent', border: 'none',
                        color: 'var(--current-text-primary)', cursor: 'pointer', fontSize: 14,
                        fontWeight: 600, textAlign: 'left', fontFamily: 'var(--font-primary)',
                      }}>
                        <span style={{ color: 'var(--color-primary-cyan)', marginRight: 8 }}>Q{i + 1}.</span>
                        {qa.question}
                        {expanded === i ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      </button>
                      {expanded === i && (
                        <div style={{
                          padding: '0 20px 16px', color: 'var(--current-text-secondary)',
                          fontSize: 14, lineHeight: 1.6, borderTop: '1px solid var(--current-border)',
                          paddingTop: 12,
                        }}>
                          {qa.answer}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </PageTransition>
    </>
  );
}
