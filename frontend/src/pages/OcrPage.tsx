import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import { generateUUID } from '../utils/uuid';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { ScanLine, Upload, ArrowLeft, Loader, Copy, FileText, Sparkles } from 'lucide-react';

const getUserId = () => {
  let uid = localStorage.getItem('pf_user_id');
  if (!uid) { uid = generateUUID(); localStorage.setItem('pf_user_id', uid); }
  return uid;
};

export default function OcrPage() {
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState('');
  const [paperId, setPaperId] = useState<string | null>(null);
  const [engine, setEngine] = useState('paddle');

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFileName(f.name);
    setFile(f);
    setExtractedText('');
    setPaperId(null);
    if (f.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (ev) => setPreview(ev.target?.result as string);
      reader.readAsDataURL(f);
    } else {
      setPreview(null);
    }
  };

  const handleExtract = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.post('/ocr/extract', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { engine },
      });
      const data = res.data?.data || res.data;
      setExtractedText(data?.text || data?.extracted_text || JSON.stringify(data));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setExtractedText(`Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadAndProcess = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.post('/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        params: { user_id: getUserId(), engine, language: 'en' },
      });
      const data = res.data?.data || res.data;
      setPaperId(data?.paper_id || null);
      setExtractedText(data?.extracted_text || data?.text || `Paper uploaded! ID: ${data?.paper_id}`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown error';
      setExtractedText(`Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => { setPreview(null); setExtractedText(''); setFileName(''); setFile(null); setPaperId(null); setEngine('paddle'); };

  return (
    <>
      <Navbar />
      <PageTransition>
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 40px 40px' }}>
          <div className="tool-header">
            <button className="btn-ghost" onClick={() => navigate('/research')}>
              <ArrowLeft size={16} /> Back
            </button>
            <div>
              <h1 style={{ display: 'flex', alignItems: 'center', gap: 12 }} className="gradient-text">
                <ScanLine size={28} /> OCR Scanner
              </h1>
              <p className="header-subtitle">Extract text from images and scanned documents</p>
            </div>
          </div>

          {/* Upload Area */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
            onClick={() => !preview && !fileName && fileRef.current?.click()}
            style={{
              width: '100%', minHeight: 260, border: '2px dashed var(--current-border)',
              borderRadius: 16, display: 'flex', flexDirection: 'column', alignItems: 'center',
              justifyContent: 'center', cursor: (preview || fileName) ? 'default' : 'pointer',
              transition: 'all 0.2s', background: 'rgba(255,255,255,0.02)', marginTop: 32,
              overflow: 'hidden',
            }}
          >
            {!preview && !fileName ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Upload size={48} style={{ color: 'var(--color-primary-cyan)', marginBottom: 16, opacity: 0.8 }} />
                <h3 style={{ marginBottom: 8 }}>Drop a file here or click to upload</h3>
                <p style={{ color: 'var(--current-text-secondary)', fontSize: 14 }}>Supports PNG, JPG, JPEG, PDF, DOCX</p>
              </div>
            ) : preview ? (
              <img src={preview} alt={fileName} style={{ maxWidth: '100%', maxHeight: 300, objectFit: 'contain', borderRadius: 8, padding: 16 }} />
            ) : (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <FileText size={48} style={{ color: 'var(--color-primary-cyan)', marginBottom: 16 }} />
                <h3>{fileName}</h3>
              </div>
            )}
          </motion.div>
          <input type="file" ref={fileRef} style={{ display: 'none' }} accept=".png,.jpg,.jpeg,.pdf,.docx" onChange={handleFile} />

          {/* Engine Selector */}
          {(preview || fileName) && (
            <div style={{ display: 'flex', gap: 12, justifyContent: 'center', alignItems: 'center', marginTop: 24 }}>
              <label style={{ fontSize: 14, color: 'var(--current-text-secondary)', fontWeight: 500 }}>Engine:</label>
              <div style={{ display: 'flex', gap: 4, background: 'var(--current-input-bg)', border: '1px solid var(--current-border)', borderRadius: 10, padding: 3 }}>
                {[
                  { id: 'paddle', label: 'PaddleOCR', icon: <ScanLine size={14} />, desc: 'Local · Free' },
                  { id: 'llm', label: 'AI Vision', icon: <Sparkles size={14} />, desc: 'Cloud · Smart' },
                ].map((eng) => (
                  <button
                    key={eng.id}
                    onClick={() => setEngine(eng.id)}
                    style={{
                      padding: '8px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
                      fontSize: 13, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6,
                      transition: 'all 0.2s',
                      background: engine === eng.id ? 'var(--color-primary-cyan)' : 'transparent',
                      color: engine === eng.id ? '#000' : 'var(--current-text-secondary)',
                      boxShadow: engine === eng.id ? '0 2px 8px rgba(0,212,255,0.3)' : 'none',
                    }}
                  >
                    {eng.icon} {eng.label}
                    <span style={{ fontSize: 10, opacity: 0.7 }}>{eng.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          {(preview || fileName) && (
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 16 }}>
              <button className="btn btn-primary" onClick={handleExtract} disabled={loading}>
                {loading ? <><Loader size={18} className="spin" /> Extracting...</> : <><ScanLine size={18} /> Extract Text</>}
              </button>
              <button className="btn btn-secondary" onClick={handleUploadAndProcess} disabled={loading}>
                <Upload size={18} /> Upload & Save Paper
              </button>
              <button className="btn btn-secondary" onClick={reset}>Reset</button>
            </div>
          )}

          {/* Paper ID */}
          {paperId && (
            <div style={{
              marginTop: 16, padding: '12px 20px', background: 'rgba(0,212,255,0.08)',
              border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8, fontSize: 14,
              color: 'var(--color-primary-cyan)', display: 'flex', alignItems: 'center', gap: 8,
            }}>
              <FileText size={16} /> Paper saved! You can now use Summarize, Translate, or Q&A tools.
              <button className="btn btn-secondary" style={{ marginLeft: 'auto', padding: '4px 10px', fontSize: 12 }}
                onClick={() => navigator.clipboard.writeText(paperId)}
              >
                <Copy size={12} /> Copy Paper ID
              </button>
            </div>
          )}

          {/* Result */}
          {extractedText && (
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              style={{
                marginTop: 32, background: 'var(--current-input-bg)', border: '1px solid var(--current-border)',
                borderRadius: 12, padding: 24, position: 'relative',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h3 style={{ fontSize: 16, fontWeight: 600 }}>Extracted Text</h3>
                <button className="btn btn-secondary" style={{ padding: '8px 14px', fontSize: 13 }}
                  onClick={() => navigator.clipboard.writeText(extractedText)}
                ><Copy size={14} /> Copy</button>
              </div>
              <p style={{ lineHeight: 1.8, whiteSpace: 'pre-wrap' }}>{extractedText}</p>
            </motion.div>
          )}
        </div>
      </PageTransition>
    </>
  );
}
