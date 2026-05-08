import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { FileText, Upload, Download, ArrowLeft, Loader, AlertCircle } from 'lucide-react';

const getUserId = () => {
  let uid = localStorage.getItem('pf_user_id');
  if (!uid) { uid = crypto.randomUUID(); localStorage.setItem('pf_user_id', uid); }
  return uid;
};

export default function SummarizePage() {
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName] = useState('');
  const [paperId, setPaperId] = useState('');
  const [error, setError] = useState('');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setUploading(true);
    setError('');
    setSummary(null);
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

  const handleSummarize = async () => {
    if (!paperId) { setError('Please upload a paper first'); return; }
    setLoading(true);
    setSummary(null);
    setError('');
    try {
      const res = await api.post('/summarize/', {
        paper_id: paperId,
        mode: 'llm',
      }, { params: { user_id: getUserId() } });
      const data = res.data?.data || res.data;
      setSummary(data?.content || data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Summarization failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!summary) return;
    const content = typeof summary === 'string' ? summary : JSON.stringify(summary, null, 2);
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
              <p className="header-subtitle">Upload a research paper and generate an AI summary</p>
            </div>
          </div>

          <div className="tool-content-grid">
            <motion.div className="tool-input-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div className="card-header">
                <h3>Upload Paper</h3>
              </div>

              {/* Upload button */}
              <div
                onClick={() => fileRef.current?.click()}
                style={{
                  border: '2px dashed var(--current-border)', borderRadius: 12, padding: 32,
                  textAlign: 'center', cursor: 'pointer', marginBottom: 16,
                  background: 'rgba(255,255,255,0.02)', transition: 'all 0.2s',
                }}
              >
                <Upload size={32} style={{ color: 'var(--color-primary-cyan)', marginBottom: 8 }} />
                <p style={{ margin: 0, fontSize: 14 }}>Click to upload PDF, DOCX, or Image</p>
              </div>
              <input type="file" ref={fileRef} style={{ display: 'none' }} accept=".pdf,.docx,.png,.jpg,.jpeg" onChange={handleFileUpload} />

              {/* File status */}
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

              <button className="btn-process" onClick={handleSummarize} disabled={loading || !paperId || uploading}>
                {loading ? <><Loader size={18} className="spin" /> Summarizing...</> : uploading ? 'Uploading paper...' : 'Generate Summary'}
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
                  <p>Upload a paper, then click "Generate Summary"</p>
                </div>
              )}
              {loading && (
                <div className="loading-output">
                  <Loader size={40} className="spin" />
                  <p>Analyzing and summarizing your paper...</p>
                </div>
              )}
              {summary && (
                <div style={{
                  padding: 24, background: 'rgba(255,255,255,0.02)', borderRadius: 12,
                  border: '1px solid var(--current-border)', lineHeight: 1.8, whiteSpace: 'pre-wrap',
                }}>
                  {typeof summary === 'string' ? summary : JSON.stringify(summary, null, 2)}
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </PageTransition>
    </>
  );
}
