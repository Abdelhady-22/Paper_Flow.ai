import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { fadeInUp } from '../utils/motion';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import {
  Upload, Search, MessageCircle, FileText, Globe, HelpCircle,
  Plus, ArrowLeft
} from 'lucide-react';

type View = 'entry' | 'upload' | 'search';

export default function ResearchPage() {
  const navigate = useNavigate();
  const [view, setView] = useState<View>('entry');

  return (
    <div style={{ minHeight: '100vh' }}>
      <Navbar />
      <PageTransition>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 40px 40px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {view === 'entry' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', paddingTop: 40, width: '100%' }}>
              <div className="tool-header" style={{ maxWidth: 800 }}>
                <button className="btn-ghost" onClick={() => navigate('/dashboard')}>
                  <ArrowLeft size={16} /> Back
                </button>
                <div>
                  <h1 className="gradient-text">Research Paper Assistant</h1>
                  <p className="header-subtitle">How would you like to get started?</p>
                </div>
              </div>

              <div className="entry-options-container" style={{ marginTop: 32 }}>
                <motion.button whileHover={{ scale: 1.02, y: -5 }} whileTap={{ scale: 0.98 }}
                  className="entry-option-btn" onClick={() => setView('upload')}
                  style={{ border: '2px solid var(--current-border)' }}
                >
                  <Upload size={40} style={{ color: 'var(--color-primary-cyan)' }} />
                  <div className="option-content">
                    <h3>I have a paper / PDF</h3>
                    <p>Upload your document to analyze, summarize, translate, or generate Q&A</p>
                  </div>
                </motion.button>

                <motion.button whileHover={{ scale: 1.02, y: -5 }} whileTap={{ scale: 0.98 }}
                  className="entry-option-btn" onClick={() => setView('search')}
                  style={{ border: '2px solid var(--current-border)' }}
                >
                  <Search size={40} style={{ color: '#8B5CF6' }} />
                  <div className="option-content">
                    <h3>Find papers for me</h3>
                    <p>Describe your research topic and let AI discover relevant papers</p>
                  </div>
                </motion.button>
              </div>
            </div>
          )}

          {view === 'upload' && (
            <div style={{ paddingTop: 40, width: '100%', maxWidth: 900 }}>
              <div className="tool-header">
                <button className="btn-ghost" onClick={() => setView('entry')}>
                  <ArrowLeft size={16} /> Back
                </button>
                <div>
                  <h1 className="gradient-text">Research Paper Assistant</h1>
                  <p className="header-subtitle">Upload your document to analyze, summarize, translate, or generate Q&A</p>
                </div>
              </div>

              {/* Upload + Chat */}
              <div className="action-cards-row" style={{ marginTop: 32, marginBottom: 32 }}>
                <motion.div whileHover={{ y: -5 }} className="action-card" onClick={() => document.getElementById('file-upload-main')?.click()}>
                  <div className="card-icon"><Upload size={24} /></div>
                  <h3>Upload Paper / PDF</h3>
                  <p>PDFs and images supported</p>
                  <input type="file" id="file-upload-main" style={{ display: 'none' }} accept=".pdf,.docx,.png,.jpg,.jpeg" />
                </motion.div>

                <motion.div whileHover={{ y: -5 }} className="action-card" onClick={() => navigate('/chat')}>
                  <div className="card-icon"><MessageCircle size={24} /></div>
                  <h3>Chat with AI</h3>
                  <p>Ask questions about your research</p>
                </motion.div>
              </div>

              {/* Quick Tools */}
              <h3 style={{ fontSize: 16, color: 'var(--current-text-secondary)', marginBottom: 16 }}>Quick Tools</h3>
              <div className="action-cards-row" style={{ marginBottom: 32 }}>
                {[
                  { icon: <FileText size={24} />, title: 'Summarization', desc: 'Summarize documents & articles', route: '/summarize' },
                  { icon: <Globe size={24} />, title: 'Translation', desc: 'Translate texts', route: '/translate' },
                  { icon: <Search size={24} />, title: 'OCR Scanner', desc: 'Extract text from images', route: '/ocr' },
                  { icon: <HelpCircle size={24} />, title: 'Q&A Generator', desc: 'Generate study questions', route: '/qa-generator' },
                ].map((tool, i) => (
                  <motion.div key={i} whileHover={{ y: -5 }} className="action-card" style={{ height: 180 }}
                    onClick={() => navigate(tool.route)}
                  >
                    <div className="card-icon">{tool.icon}</div>
                    <h3 style={{ fontSize: 16 }}>{tool.title}</h3>
                    <p>{tool.desc}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {view === 'search' && (
            <div style={{ paddingTop: 40, width: '100%', maxWidth: 900 }}>
              <div className="tool-header">
                <button className="btn-ghost" onClick={() => setView('entry')}>
                  <ArrowLeft size={16} /> Back
                </button>
                <div>
                  <h1 className="gradient-text">Find Papers for Me</h1>
                  <p className="header-subtitle">Describe your research topic and let AI discover relevant papers</p>
                </div>
              </div>

              <div style={{ width: '100%', marginTop: 32 }}>
                {[
                  { label: 'Paper Name (optional)', placeholder: 'e.g., COVID-19 vaccine efficacy study' },
                  { label: 'Research Field', placeholder: 'e.g., Machine Learning, NLP' },
                ].map((field, i) => (
                  <div key={i} style={{ marginBottom: 20 }}>
                    <label style={{ display: 'block', marginBottom: 8, color: 'var(--current-text-secondary)', fontSize: 14 }}>
                      {field.label}
                    </label>
                    <input type="text" placeholder={field.placeholder} style={{
                      width: '100%', padding: '14px 16px', background: 'var(--current-surface)',
                      border: '1px solid var(--current-border)', borderRadius: 8,
                      color: 'var(--current-text-primary)', fontSize: 15, outline: 'none',
                      fontFamily: 'var(--font-primary)',
                    }} />
                  </div>
                ))}
                <div style={{ marginBottom: 24 }}>
                  <label style={{ display: 'block', marginBottom: 8, color: 'var(--current-text-secondary)', fontSize: 14 }}>
                    Description / Keywords
                  </label>
                  <textarea placeholder="Describe what you are looking for..." rows={4} style={{
                    width: '100%', padding: '14px 16px', background: 'var(--current-surface)',
                    border: '1px solid var(--current-border)', borderRadius: 8,
                    color: 'var(--current-text-primary)', fontSize: 15, resize: 'vertical',
                    outline: 'none', fontFamily: 'var(--font-primary)',
                  }} />
                </div>
                <button className="btn btn-primary" style={{ width: '100%', padding: 16, fontSize: 16 }}>
                  <Search size={20} /> Find Papers
                </button>
              </div>
            </div>
          )}
        </div>
      </PageTransition>
    </div>
  );
}
