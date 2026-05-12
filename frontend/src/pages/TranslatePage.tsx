import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import { generateUUID } from '../utils/uuid';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { Languages, ArrowLeft, Loader, Copy, ArrowLeftRight, Upload, FileText, AlertCircle } from 'lucide-react';

const getUserId = () => {
  let uid = localStorage.getItem('pf_user_id');
  if (!uid) { uid = generateUUID(); localStorage.setItem('pf_user_id', uid); }
  return uid;
};

export default function TranslatePage() {
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [direction, setDirection] = useState<'en-ar' | 'ar-en'>('en-ar');
  const [fileName, setFileName] = useState('');
  const [paperId, setPaperId] = useState('');
  const [error, setError] = useState('');

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    setUploading(true);
    setError('');
    setResult('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.post('/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { user_id: getUserId(), engine: 'paddle', language: direction === 'ar-en' ? 'ar' : 'en' },
      });
      const data = res.data?.data || res.data;
      setPaperId(data?.paper_id || '');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleTranslate = async () => {
    if (!paperId) { setError('Please upload a paper first'); return; }
    setLoading(true);
    setResult('');
    setError('');
    try {
      const res = await api.post('/translate/', {
        paper_id: paperId,
        direction,
        mode: 'llm',
      }, { params: { user_id: getUserId() } });
      const data = res.data?.data || res.data;
      setResult(data?.content || data?.translated_text || JSON.stringify(data));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Translation failed');
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
              <p className="header-subtitle">Translate research papers between English and Arabic</p>
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

              <button className="btn-process" onClick={handleTranslate} disabled={loading || !paperId || uploading}>
                {loading ? <><Loader size={18} className="spin" /> Translating...</> : uploading ? 'Uploading paper...' : 'Translate'}
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
                  <p>Upload a paper, then click "Translate"</p>
                </div>
              )}
              {loading && (
                <div className="loading-output">
                  <Loader size={40} className="spin" />
                  <p>Translating your paper...</p>
                </div>
              )}
              {result && (
                <div style={{
                  padding: 24, background: 'rgba(255,255,255,0.02)', borderRadius: 12,
                  border: '1px solid var(--current-border)', lineHeight: 1.8,
                  direction: direction === 'en-ar' ? 'rtl' : 'ltr',
                  fontFamily: direction === 'en-ar' ? 'var(--font-arabic)' : 'var(--font-primary)',
                  fontSize: 16, whiteSpace: 'pre-wrap',
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
