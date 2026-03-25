import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import api from '../api/client';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { ScanLine, Upload, ArrowLeft, Loader, Copy, FileText } from 'lucide-react';

export default function OcrPage() {
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [extractedText, setExtractedText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [fileName, setFileName] = useState('');

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFileName(f.name);
    setFile(f);
    setExtractedText('');
    const reader = new FileReader();
    reader.onload = (ev) => setPreview(ev.target?.result as string);
    reader.readAsDataURL(f);
  };

  const handleExtract = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.post('/ocr/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setExtractedText(res.data.text || res.data.extracted_text || JSON.stringify(res.data));
    } catch {
      setExtractedText('Backend is unavailable. Please ensure the gateway is running on port 8000.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => { setPreview(null); setExtractedText(''); setFileName(''); setFile(null); };

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
            onClick={() => !preview && fileRef.current?.click()}
            style={{
              width: '100%', minHeight: 260, border: '2px dashed var(--current-border)',
              borderRadius: 16, display: 'flex', flexDirection: 'column', alignItems: 'center',
              justifyContent: 'center', cursor: preview ? 'default' : 'pointer',
              transition: 'all 0.2s', background: 'rgba(255,255,255,0.02)', marginTop: 32,
              overflow: 'hidden',
            }}
          >
            {!preview ? (
              <div style={{ textAlign: 'center', padding: 40 }}>
                <Upload size={48} style={{ color: 'var(--color-primary-cyan)', marginBottom: 16, opacity: 0.8 }} />
                <h3 style={{ marginBottom: 8 }}>Drop an image here or click to upload</h3>
                <p style={{ color: 'var(--current-text-secondary)', fontSize: 14 }}>Supports PNG, JPG, JPEG, PDF</p>
              </div>
            ) : (
              <img src={preview} alt={fileName} style={{ maxWidth: '100%', maxHeight: 300, objectFit: 'contain', borderRadius: 8, padding: 16 }} />
            )}
          </motion.div>
          <input type="file" ref={fileRef} style={{ display: 'none' }} accept=".png,.jpg,.jpeg,.pdf" onChange={handleFile} />

          {/* Actions */}
          {preview && (
            <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 24 }}>
              <button className="btn btn-primary" onClick={handleExtract} disabled={loading}>
                {loading ? <><Loader size={18} className="spin" /> Extracting...</> : <><ScanLine size={18} /> Extract Text</>}
              </button>
              <button className="btn btn-secondary" onClick={reset}>Reset</button>
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
