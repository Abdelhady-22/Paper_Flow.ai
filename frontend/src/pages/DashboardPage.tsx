import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { staggerContainer, fadeInUp } from '../utils/motion';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import {
  MessageCircle, FileText, Upload, Search, Languages,
  HelpCircle, Zap, Globe
} from 'lucide-react';

const tools = [
  { id: 'chatbot', icon: <MessageCircle size={24} />, title: 'AI Chat', desc: 'Chat with your research papers using RAG-powered AI.', route: '/chat' },
  { id: 'research', icon: <FileText size={24} />, title: 'Research Assistant', desc: 'Analyze, summarize, translate your papers.', route: '/research' },
  { id: 'upload', icon: <Upload size={24} />, title: 'Upload Paper', desc: 'Upload PDFs and images for OCR processing.', route: '/research' },
  { id: 'summarize', icon: <FileText size={24} />, title: 'Summarization', desc: 'Summarize documents and articles with AI.', route: '/summarize' },
  { id: 'translate', icon: <Globe size={24} />, title: 'Translation', desc: 'Translate texts between English and Arabic.', route: '/translate' },
  { id: 'discover', icon: <Search size={24} />, title: 'Discover Papers', desc: 'Find papers from Semantic Scholar.', route: '/discover' },
];

const quickActions = [
  { icon: <MessageCircle size={24} />, title: 'AI Chat', desc: 'Start chatting with your papers.', route: '/chat' },
  { icon: <FileText size={24} />, title: 'Research Assistant', desc: 'Analyze and process papers.', route: '/research' },
  { icon: <Search size={24} />, title: 'Discover', desc: 'Find new research papers.', route: '/discover' },
];

export default function DashboardPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'overview' | 'tools' | 'activity'>('overview');

  return (
    <div>
      <Navbar />
      <PageTransition>
        <motion.div initial="hidden" animate="show" variants={staggerContainer}
          style={{ maxWidth: 1200, margin: '0 auto', padding: '0 40px 40px' }}
        >
          {/* Hero */}
          <motion.div variants={fadeInUp} style={{
            padding: '48px 40px', borderRadius: 20, marginTop: 32, marginBottom: 32,
            background: 'linear-gradient(135deg, rgba(0,212,255,0.08) 0%, rgba(10,22,40,0.5) 100%)',
            border: '1px solid rgba(0,212,255,0.15)',
          }}>
            <h1 style={{ fontSize: '2.4rem', fontWeight: 800, lineHeight: 1.1, marginBottom: 12 }}>
              Welcome to <span className="gradient-text">Paper Flow AI</span>
            </h1>
            <p style={{ color: 'var(--current-text-secondary)', fontSize: 16 }}>
              Your AI-powered research paper assistant. Select a tool below to get started.
            </p>
          </motion.div>

          {/* Tabs */}
          <motion.div variants={fadeInUp} style={{ marginBottom: 32 }}>
            <div className="tabs-nav">
              {(['overview', 'tools', 'activity'] as const).map(tab => (
                <button key={tab} className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Overview */}
          {activeTab === 'overview' && (
            <motion.div variants={staggerContainer} initial="hidden" animate="show">
              <motion.h3 variants={fadeInUp} style={{ fontSize: 18, fontWeight: 600, marginBottom: 20, color: 'var(--current-text-secondary)' }}>
                Quick Actions
              </motion.h3>
              <div style={{ display: 'flex', gap: 20, marginBottom: 48 }}>
                {quickActions.map((action, i) => (
                  <motion.div key={i} variants={fadeInUp} whileHover={{ y: -5 }}
                    className="card card-glow" style={{ flex: 1, padding: 32, cursor: 'pointer', textAlign: 'center' }}
                    onClick={() => navigate(action.route)}
                  >
                    <div className="card-icon" style={{ margin: '0 auto 12px' }}>{action.icon}</div>
                    <h4 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>{action.title}</h4>
                    <p style={{ color: 'var(--current-text-secondary)', fontSize: 14, margin: 0 }}>{action.desc}</p>
                  </motion.div>
                ))}
              </div>

              <motion.h3 variants={fadeInUp} style={{ fontSize: 18, fontWeight: 600, marginBottom: 20, color: 'var(--current-text-secondary)' }}>
                Recent Activity
              </motion.h3>
              <motion.div variants={fadeInUp} style={{ padding: 20, color: 'var(--current-text-secondary)', opacity: 0.6 }}>
                No activity yet. Start using tools to see your history.
              </motion.div>
            </motion.div>
          )}

          {/* Tools */}
          {activeTab === 'tools' && (
            <motion.div variants={staggerContainer} initial="hidden" animate="show">
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
                {tools.map(tool => (
                  <motion.div key={tool.id} variants={fadeInUp} whileHover={{ y: -5 }}
                    className="card card-glow" style={{ padding: 32, cursor: 'pointer' }}
                  >
                    <div className="card-icon">{tool.icon}</div>
                    <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>{tool.title}</h3>
                    <p style={{ color: 'var(--current-text-secondary)', fontSize: 14, marginBottom: 16 }}>{tool.desc}</p>
                    <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => navigate(tool.route)}>
                      Open Tool
                    </button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {/* Activity */}
          {activeTab === 'activity' && (
            <motion.div variants={fadeInUp} initial="hidden" animate="show">
              <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 20 }}>Activity History</h3>
              <div style={{ textAlign: 'center', padding: 40, color: 'var(--current-text-secondary)' }}>
                No recent activity found.
              </div>
            </motion.div>
          )}
        </motion.div>
      </PageTransition>
    </div>
  );
}
