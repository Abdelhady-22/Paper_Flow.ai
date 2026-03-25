import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTheme } from '../context/ThemeContext';
import { staggerContainer, fadeInUp } from '../utils/motion';
import {
  MessageCircle, FileText, Languages, HelpCircle, Search,
  Shield, Heart, ArrowRight, Sparkles, Sun, Moon, Globe
} from 'lucide-react';

const features = [
  { icon: <MessageCircle size={28} />, title: 'AI Chat with Papers', desc: 'Get cited answers from your research papers using RAG-powered AI.' },
  { icon: <FileText size={28} />, title: 'Smart Summarization', desc: 'Get concise summaries using local models or cloud LLMs.' },
  { icon: <Languages size={28} />, title: 'EN ↔ AR Translation', desc: 'Translate papers between English and Arabic with neural MT.' },
  { icon: <HelpCircle size={28} />, title: 'Q&A Generation', desc: 'Auto-generate question-answer pairs for study guides.' },
  { icon: <Search size={28} />, title: 'Paper Discovery', desc: 'AI-powered pipeline to find, download, and import papers.' },
];

export default function WelcomePage() {
  const navigate = useNavigate();
  const { theme, changeTheme } = useTheme();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', position: 'relative' }}>
      {/* Floating Controls */}
      <div style={{ position: 'fixed', top: 20, right: 20, display: 'flex', gap: 12, zIndex: 1000 }}>
        <button className="btn-ghost" onClick={() => changeTheme(theme === 'dark' ? 'light' : 'dark')}
          style={{ display: 'flex', alignItems: 'center', gap: 6 }}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>

      {/* Hero */}
      <motion.div initial="hidden" animate="show" variants={staggerContainer} style={{ textAlign: 'center', maxWidth: 700 }}>
        <motion.div variants={fadeInUp} style={{ marginBottom: 24 }}>
          <div style={{
            width: 80, height: 80, borderRadius: 20, margin: '0 auto 24px',
            background: 'linear-gradient(135deg, #00D4FF, #00A8CC)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 8px 32px rgba(0, 212, 255, 0.3)',
          }}>
            <FileText size={36} color="#fff" />
          </div>
        </motion.div>

        <motion.h1 variants={fadeInUp} style={{ fontSize: '3.5rem', fontWeight: 800, lineHeight: 1.1, marginBottom: 16, letterSpacing: -1 }}>
          Welcome to{' '}
          <span className="gradient-text">Paper Flow AI</span>
        </motion.h1>

        <motion.p variants={fadeInUp} style={{ fontSize: 18, color: 'var(--current-text-secondary)', marginBottom: 40, lineHeight: 1.6 }}>
          Your AI-powered research paper assistant. Upload papers, chat with AI,
          summarize, translate, generate Q&A, and discover new research.
        </motion.p>

        <motion.div variants={fadeInUp}>
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/dashboard')} style={{ fontSize: 18, padding: '16px 40px' }}>
            Get Started <ArrowRight size={20} />
          </button>
        </motion.div>
      </motion.div>

      {/* Features */}
      <motion.div initial="hidden" animate="show" variants={staggerContainer}
        style={{ display: 'flex', flexWrap: 'wrap', gap: 20, maxWidth: 900, marginTop: 64, justifyContent: 'center' }}
      >
        {features.map((f, i) => (
          <motion.div key={i} variants={fadeInUp} className="card" style={{
            padding: 24, width: 260, textAlign: 'center', cursor: 'default',
          }}>
            <div className="card-icon" style={{ margin: '0 auto 12px' }}>{f.icon}</div>
            <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>{f.title}</h3>
            <p style={{ fontSize: 13, color: 'var(--current-text-secondary)', margin: 0, lineHeight: 1.5 }}>{f.desc}</p>
          </motion.div>
        ))}
      </motion.div>

      {/* Trust Badges */}
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }}
        style={{ display: 'flex', gap: 24, marginTop: 48 }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--current-text-secondary)', fontSize: 14 }}>
          <Shield size={16} /> <span>Privacy First</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--current-text-secondary)', fontSize: 14 }}>
          <Heart size={16} /> <span>Built for Researchers</span>
        </div>
      </motion.div>
    </div>
  );
}
