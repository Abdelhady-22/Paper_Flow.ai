import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import {
  MessageSquare, BookOpen, Languages, HelpCircle, Search, Mic,
  Download, Shield, Zap, ArrowRight, Sparkles, FileText, Globe,
  Brain, Bot
} from 'lucide-react';

const features = [
  {
    icon: MessageSquare,
    title: 'AI Chat with Papers',
    desc: 'Ask questions and get cited answers from your research papers using RAG-powered AI.',
    color: 'from-violet-500 to-purple-600',
    glow: 'rgba(139, 92, 246, 0.2)',
  },
  {
    icon: BookOpen,
    title: 'Smart Summarization',
    desc: 'Get concise summaries using local AI models or cloud LLMs — your choice.',
    color: 'from-cyan-500 to-blue-600',
    glow: 'rgba(34, 211, 238, 0.2)',
  },
  {
    icon: Languages,
    title: 'EN ↔ AR Translation',
    desc: 'Translate papers between English and Arabic with neural machine translation.',
    color: 'from-emerald-500 to-teal-600',
    glow: 'rgba(52, 211, 153, 0.2)',
  },
  {
    icon: HelpCircle,
    title: 'Q&A Generation',
    desc: 'Auto-generate question-answer pairs for study guides and comprehension.',
    color: 'from-amber-500 to-orange-600',
    glow: 'rgba(251, 191, 36, 0.2)',
  },
  {
    icon: Search,
    title: 'Paper Discovery',
    desc: 'AI-powered pipeline: find, download, and import papers from Semantic Scholar.',
    color: 'from-rose-500 to-pink-600',
    glow: 'rgba(251, 113, 133, 0.2)',
  },
  {
    icon: Mic,
    title: 'Voice Interaction',
    desc: 'Speak your questions and listen to answers with multi-provider STT/TTS.',
    color: 'from-sky-500 to-indigo-600',
    glow: 'rgba(56, 189, 248, 0.2)',
  },
];

const stats = [
  { value: '3', label: 'OCR Engines' },
  { value: '5', label: 'AI Agents' },
  { value: '6+', label: 'LLM Providers' },
  { value: '3', label: 'Export Formats' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      <Navbar />

      {/* Orb backgrounds */}
      <div className="orb w-[500px] h-[500px] bg-[var(--accent)] top-[-150px] left-[-100px]" />
      <div className="orb w-[400px] h-[400px] bg-[var(--cyan)] top-[200px] right-[-100px]" />
      <div className="orb w-[300px] h-[300px] bg-purple-600 bottom-[100px] left-[30%]" />

      {/* ── Hero ────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="animate-fade-in-down">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--accent)]/10 border border-[var(--accent)]/20 text-[var(--accent-light)] text-sm font-medium mb-8">
              <Sparkles size={14} />
              AI-Powered Research Assistant
            </div>
          </div>

          <h1 className="text-5xl md:text-7xl font-black leading-tight mb-6 animate-fade-in delay-100">
            Your Research,{' '}
            <span className="gradient-text">Supercharged</span>
          </h1>

          <p className="text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-10 animate-fade-in delay-200">
            Upload papers, chat with AI, summarize, translate, generate Q&A, and discover
            new research — all in one beautiful platform.
          </p>

          <div className="flex items-center justify-center gap-4 animate-fade-in delay-300">
            <Link to="/chat" className="btn btn-primary btn-lg group">
              <MessageSquare size={18} />
              Start Chatting
              <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link to="/discover" className="btn btn-secondary btn-lg">
              <Globe size={18} />
              Discover Papers
            </Link>
          </div>
        </div>
      </section>

      {/* ── Stats ───────────────────────────────────────────── */}
      <section className="relative py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass p-6 grid grid-cols-2 md:grid-cols-4 gap-6 animate-fade-in delay-400">
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl font-black gradient-text mb-1">{stat.value}</div>
                <div className="text-sm text-[var(--text-secondary)]">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features Grid ───────────────────────────────────── */}
      <section className="relative py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-4 animate-fade-in">
              Everything You Need for <span className="gradient-text">Research</span>
            </h2>
            <p className="text-[var(--text-secondary)] max-w-lg mx-auto animate-fade-in delay-100">
              A complete toolkit powered by AI to accelerate your academic workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => (
              <div
                key={i}
                className={`card p-6 animate-slide-up delay-${(i + 1) * 100}`}
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div
                  className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4`}
                  style={{ boxShadow: `0 4px 20px ${f.glow}` }}
                >
                  <f.icon size={22} className="text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2">{f.title}</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── How It Works ────────────────────────────────────── */}
      <section className="relative py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It <span className="gradient-text">Works</span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { step: '01', icon: FileText, title: 'Upload', desc: 'Upload your PDF or DOCX papers. OCR extracts text automatically.' },
              { step: '02', icon: Brain, title: 'Process', desc: 'AI analyzes, embeds, and indexes your papers in the vector database.' },
              { step: '03', icon: Bot, title: 'Interact', desc: 'Chat, summarize, translate, generate Q&A, or discover new papers.' },
            ].map((item, i) => (
              <div key={i} className="card p-6 text-center animate-slide-up" style={{ animationDelay: `${i * 150}ms` }}>
                <div className="text-4xl font-black text-[var(--accent)]/20 mb-3">{item.step}</div>
                <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-br from-[var(--accent)] to-[var(--cyan)] flex items-center justify-center mb-4">
                  <item.icon size={24} className="text-white" />
                </div>
                <h3 className="text-lg font-bold mb-2">{item.title}</h3>
                <p className="text-sm text-[var(--text-secondary)]">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────── */}
      <section className="relative py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="glass p-12 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to <span className="gradient-text">Transform</span> Your Research?
            </h2>
            <p className="text-[var(--text-secondary)] mb-8 max-w-md mx-auto">
              Start uploading papers and chatting with your AI research assistant today.
            </p>
            <Link to="/chat" className="btn btn-primary btn-lg inline-flex">
              <Sparkles size={18} />
              Get Started
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────── */}
      <footer className="border-t border-[var(--border)] py-8 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between text-sm text-[var(--text-tertiary)]">
          <span>Paper Flow AI</span>
          <span>Built with FastAPI, React & AI</span>
        </div>
      </footer>
    </div>
  );
}
