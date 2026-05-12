import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import { generateUUID } from '../utils/uuid';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { HelpCircle, ArrowLeft, Loader, Download, ChevronDown, ChevronUp, Upload, FileText, AlertCircle } from 'lucide-react';

interface QA {
  question: string;
  answer: string;
}

const getUserId = () => {
  let uid = localStorage.getItem('pf_user_id');
  if (!uid) { uid = generateUUID(); localStorage.setItem('pf_user_id', uid); }
  return uid;
};

export default function QaGeneratorPage() {
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [qaList, setQaList] = useState<QA[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [expanded, setExpanded] = useState<number | null>(null);
  const [count, setCount] = useState(5);
  const [fileName, setFileName] = useState('');
  const [paperId, setPaperId] = useState('');
  const [error, setError] = useState('');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setUploading(true);
    setError('');
    setQaList([]);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.post('/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { user_id: getUserId(), engine: 'paddle', language: 'en' },
      });
      const data = res.data?.data || res.data;
      setPaperId(data?.paper_id || '');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleGenerate = async () => {
    if (!paperId) { setError('Please upload a paper first'); return; }
    setLoading(true);
    setQaList([]);
    setError('');
    try {
      const res = await api.post('/qa/generate', {
        paper_id: paperId,
        mode: 'llm',
        num_questions: count,
      }, { params: { user_id: getUserId() } });
      const data = res.data?.data || res.data;
      const pairs = data?.qa_pairs || data?.questions || [];
      if (Array.isArray(pairs)) {
        setQaList(pairs.map((p: any) => ({ question: p.question || p.q, answer: p.answer || p.a })));
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Q&A generation failed');
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
              <p className="header-subtitle">Auto-generate question-answer pairs from research papers</p>
            </div>
          </div>

          <div className="tool-content-grid">
            <motion.div className="tool-input-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="card-header">
                <h3>Upload Paper</h3>
              </div>

              <div onClick={() => fileRef.current?.click()} style={{
                border: '2px dashed var(--current-border)', borderRadius: 12, padding: 32,
                textAlign: 'center', cursor: 'pointer', marginBottom: 16,
                background: 'rgba(255,255,255,0.02)',
              }}>
                <Upload size={32} style={{ color: 'var(--color-primary-cyan)', marginBottom: 8 }} />
                <p style={{ margin: 0, fontSize: 14 }}>Click to upload PDF, DOCX, or Image</p>
              </div>
              <input type="file" ref={fileRef} style={{ display: 'none' }} accept=".pdf,.docx,.png,.jpg,.jpeg" onChange={handleFileUpload} />

              {fileName && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', background: 'rgba(0,212,255,0.08)', borderRadius: 8, marginBottom: 12, fontSize: 13, color: 'var(--color-primary-cyan)' }}>
                  <FileText size={14} /> {fileName}
                  {uploading && <Loader size={14} className="spin" />}
                  {paperId && <span style={{ marginLeft: 'auto', color: 'var(--color-success)' }}>✓ Ready</span>}
                </div>
              )}

              {error && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', background: 'rgba(255,50,50,0.08)', borderRadius: 8, marginBottom: 12, fontSize: 13, color: '#ff6b6b' }}>
                  <AlertCircle size={14} /> {error}
                </div>
              )}

              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                <label style={{ fontSize: 14, color: 'var(--current-text-secondary)' }}>Questions:</label>
                <select value={count} onChange={e => setCount(Number(e.target.value))} style={{
                  background: 'var(--current-input-bg)', border: '1px solid var(--current-border)',
                  borderRadius: 8, padding: '8px 12px', color: 'var(--current-text-primary)',
                  fontSize: 14, outline: 'none', fontFamily: 'var(--font-primary)',
                }}>
                  {[3, 5, 10, 15].map(n => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>

              <button className="btn-process" onClick={handleGenerate} disabled={loading || !paperId || uploading}>
                {loading ? <><Loader size={18} className="spin" /> Generating...</> : uploading ? 'Uploading paper...' : 'Generate Q&A'}
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
                  <p>Upload a paper, then click "Generate Q&A"</p>
                </div>
              )}
              {loading && (
                <div className="loading-output">
                  <Loader size={40} className="spin" />
                  <p>Generating questions from your paper...</p>
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
