import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { FileText, Upload, Download, ArrowLeft, Loader } from 'lucide-react';

export default function SummarizePage() {
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [inputText, setInputText] = useState('');
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
      const reader = new FileReader();
      reader.onload = (ev) => setInputText(ev.target?.result as string);
      reader.readAsText(file);
    }
  };

  const handleSummarize = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setSummary(null);
    try {
      const res = await api.post('/summarize/', { text: inputText });
      const data = res.data;
      setSummary(data.summary || data.sections || {
        background: data.background || data.text || JSON.stringify(data),
        methods: data.methods || '',
        findings: data.findings || '',
        conclusions: data.conclusions || '',
      });
    } catch {
      setSummary({
        background: 'Backend is unavailable. Please ensure the gateway is running on port 8000.',
        methods: '', findings: '', conclusions: '',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!summary) return;
    const content = `SUMMARY\n========\n\nBackground:\n${summary.background}\n\nMethods:\n${summary.methods}\n\nFindings:\n${summary.findings}\n\nConclusions:\n${summary.conclusions}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = 'summary.txt'; a.click();
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
                <FileText size={28} /> Text Summarizer
              </h1>
              <p className="header-subtitle">Summarize documents, articles, and research papers with AI</p>
            </div>
          </div>

          <div className="tool-content-grid">
            <motion.div className="tool-input-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="card-header">
                <h3>Input Text</h3>
                <button className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: 13 }}
                  onClick={() => fileRef.current?.click()}
                >
                  <Upload size={14} /> Upload File
                </button>
                <input type="file" ref={fileRef} style={{ display: 'none' }} accept=".txt,.doc,.docx" onChange={handleFileUpload} />
              </div>
              {fileName && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', background: 'rgba(0,212,255,0.08)', borderRadius: 8, marginBottom: 12, fontSize: 13, color: 'var(--color-primary-cyan)' }}>
                  <FileText size={14} /> {fileName}
                </div>
              )}
              <textarea className="tool-textarea" placeholder="Paste your text here or upload a file..."
                value={inputText} onChange={e => setInputText(e.target.value)} rows={12}
              />
              <button className="btn-process" onClick={handleSummarize} disabled={loading || !inputText.trim()}>
                {loading ? <><Loader size={18} className="spin" /> Summarizing...</> : 'Generate Summary'}
              </button>
            </motion.div>

            <motion.div className="tool-output-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <div className="card-header">
                <h3>Summary</h3>
                {summary && (
                  <button className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: 13 }} onClick={handleDownload}>
                    <Download size={14} /> Download
                  </button>
                )}
              </div>
              {!summary && !loading && (
                <div className="empty-output">
                  <FileText size={48} />
                  <p>Your summary will appear here</p>
                </div>
              )}
              {loading && (
                <div className="loading-output">
                  <Loader size={40} className="spin" />
                  <p>Analyzing and summarizing your content...</p>
                </div>
              )}
              {summary && (
                <div>
                  {[
                    { title: 'Background', text: summary.background },
                    { title: 'Methods', text: summary.methods },
                    { title: 'Key Findings', text: summary.findings },
                    { title: 'Conclusions', text: summary.conclusions },
                  ].map((s, i) => (
                    <div key={i} className="summary-section">
                      <h4>{s.title}</h4>
                      <p>{s.text}</p>
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
