import { useState } from 'react';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { setSummaryResult, setTranslationResult, setQaResult, setProcessing } from '../store/slices/paperSlice';
import api from '../api/client';
import toast from 'react-hot-toast';
import { saveAs } from 'file-saver';
import Navbar from '../components/Navbar';
import {
  BookOpen, Languages, HelpCircle, Download, Loader2, FileText,
  ArrowRightLeft, Sparkles, Cpu, Cloud, CheckCircle2
} from 'lucide-react';

const USER_ID = '00000000-0000-0000-0000-000000000001';

const tools = [
  {
    key: 'summary' as const,
    title: 'Summarization',
    desc: 'Get a concise summary of your paper\'s key findings and contributions.',
    icon: BookOpen,
    color: 'from-cyan-500 to-blue-600',
    glow: 'rgba(34, 211, 238, 0.15)',
  },
  {
    key: 'translate' as const,
    title: 'Translation',
    desc: 'Translate your paper between English and Arabic using neural MT.',
    icon: ArrowRightLeft,
    color: 'from-emerald-500 to-teal-600',
    glow: 'rgba(52, 211, 153, 0.15)',
  },
  {
    key: 'qa' as const,
    title: 'Q&A Generation',
    desc: 'Auto-generate question-answer pairs for study guides.',
    icon: HelpCircle,
    color: 'from-amber-500 to-orange-600',
    glow: 'rgba(251, 191, 36, 0.15)',
  },
];

export default function ToolsPage() {
  const dispatch = useAppDispatch();
  const { activePaperId, processing, summaryResult, translationResult, qaResult } = useAppSelector((s) => s.paper);
  const { papers } = useAppSelector((s) => s.paper);
  const [activeTool, setActiveTool] = useState<'summary' | 'translate' | 'qa' | null>(null);
  const [mode, setMode] = useState<'model' | 'llm'>('model');
  const [translateDir, setTranslateDir] = useState('en-ar');
  const [qaCount, setQaCount] = useState(5);
  const [exportFormat, setExportFormat] = useState<'txt' | 'docx' | 'pdf'>('pdf');

  const handleRun = async () => {
    if (!activePaperId) return toast.error('Select a paper first from the Chat page sidebar');
    if (!activeTool) return;

    dispatch(setProcessing(true));
    try {
      if (activeTool === 'summary') {
        const res = await api.post(`/summarize/?user_id=${USER_ID}`, { paper_id: activePaperId, mode });
        dispatch(setSummaryResult(res.data.data));
      } else if (activeTool === 'translate') {
        const res = await api.post(`/translate/?user_id=${USER_ID}`, { paper_id: activePaperId, direction: translateDir, mode });
        dispatch(setTranslationResult(res.data.data));
      } else {
        const res = await api.post(`/qa/generate?user_id=${USER_ID}`, { paper_id: activePaperId, mode, num_questions: qaCount });
        dispatch(setQaResult(res.data.data));
      }
      toast.success('Done!');
    } catch (err: any) { toast.error(err.message); }
    dispatch(setProcessing(false));
  };

  const currentResult = activeTool === 'summary' ? summaryResult : activeTool === 'translate' ? translationResult : qaResult;

  const handleExport = async () => {
    if (!currentResult) return toast.error('Generate a result first');
    try {
      const res = await api.post('/export/', { content: currentResult.content, format: exportFormat, title: `${activeTool}_result`, language: translateDir === 'en-ar' ? 'ar' : 'en' }, { responseType: 'blob' });
      saveAs(new Blob([res.data]), `${activeTool}_result.${exportFormat}`);
      toast.success(`Exported as ${exportFormat.toUpperCase()}`);
    } catch (err: any) { toast.error(err.message); }
  };

  const selectedPaper = papers.find((p) => p.paper_id === activePaperId);

  return (
    <div className="min-h-screen">
      <Navbar />

      <div className="pt-24 pb-16 px-6">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12 animate-fade-in-down">
            <h1 className="text-4xl font-bold mb-3">
              NLP <span className="gradient-text">Tools</span>
            </h1>
            <p className="text-[var(--text-secondary)] max-w-md mx-auto">
              Process your papers with powerful AI models. Choose between local models or cloud LLMs.
            </p>
            {selectedPaper && (
              <div className="inline-flex items-center gap-2 mt-4 px-4 py-2 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20 text-sm">
                <FileText size={14} className="text-[var(--accent)]" />
                <span className="text-[var(--accent-light)]">{selectedPaper.filename}</span>
                <CheckCircle2 size={14} className="text-emerald-400" />
              </div>
            )}
          </div>

          {/* Tool Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
            {tools.map((tool, i) => (
              <button
                key={tool.key}
                onClick={() => setActiveTool(tool.key)}
                className={`card p-6 text-left transition-all animate-slide-up ${
                  activeTool === tool.key ? 'ring-2 ring-[var(--accent)] bg-[var(--bg-card-hover)]' : ''
                }`}
                style={{ animationDelay: `${i * 100}ms` }}
              >
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${tool.color} flex items-center justify-center mb-4`} style={{ boxShadow: `0 4px 20px ${tool.glow}` }}>
                  <tool.icon size={24} className="text-white" />
                </div>
                <h3 className="text-lg font-bold mb-1">{tool.title}</h3>
                <p className="text-sm text-[var(--text-secondary)]">{tool.desc}</p>
              </button>
            ))}
          </div>

          {/* Config Panel */}
          {activeTool && (
            <div className="glass p-8 mb-10 animate-slide-up">
              <div className="max-w-2xl mx-auto">
                <div className="flex items-center gap-3 mb-6">
                  <Sparkles size={18} className="text-[var(--accent)]" />
                  <h3 className="text-lg font-bold">Configuration</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Mode */}
                  <div>
                    <label className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-widest mb-3 block">Processing Mode</label>
                    <div className="flex gap-2">
                      {([
                        { val: 'model' as const, label: 'Local Model', icon: Cpu, desc: 'Fast, offline' },
                        { val: 'llm' as const, label: 'Cloud LLM', icon: Cloud, desc: 'More accurate' },
                      ]).map((m) => (
                        <button key={m.val} onClick={() => setMode(m.val)}
                          className={`flex-1 p-3 rounded-xl text-left transition-all border ${
                            mode === m.val
                              ? 'bg-[var(--accent)]/10 border-[var(--accent)]/30 text-[var(--accent-light)]'
                              : 'bg-[var(--bg-input)] border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--border-hover)]'
                          }`}>
                          <m.icon size={16} className="mb-1" />
                          <div className="text-sm font-semibold">{m.label}</div>
                          <div className="text-[10px] opacity-70">{m.desc}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Extra Config */}
                  <div>
                    {activeTool === 'translate' && (
                      <>
                        <label className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-widest mb-3 block">Direction</label>
                        <div className="flex gap-2">
                          {[{ val: 'en-ar', label: '🇬🇧 → 🇸🇦 EN to AR' }, { val: 'ar-en', label: '🇸🇦 → 🇬🇧 AR to EN' }].map((d) => (
                            <button key={d.val} onClick={() => setTranslateDir(d.val)}
                              className={`flex-1 py-3 rounded-xl text-sm font-medium transition-all border ${
                                translateDir === d.val
                                  ? 'bg-[var(--accent)]/10 border-[var(--accent)]/30 text-[var(--accent-light)]'
                                  : 'bg-[var(--bg-input)] border-[var(--border)] text-[var(--text-secondary)]'
                              }`}>{d.label}</button>
                          ))}
                        </div>
                      </>
                    )}
                    {activeTool === 'qa' && (
                      <>
                        <label className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-widest mb-3 block">Number of Questions</label>
                        <input type="number" min={1} max={20} value={qaCount} onChange={(e) => setQaCount(Number(e.target.value))}
                          className="w-full bg-[var(--bg-input)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm outline-none focus:border-[var(--accent)] transition-colors"
                        />
                      </>
                    )}
                  </div>
                </div>

                <button onClick={handleRun} disabled={processing || !activePaperId} className="btn btn-primary btn-lg w-full mt-6">
                  {processing ? <Loader2 size={18} className="animate-spin" /> : <Sparkles size={18} />}
                  {processing ? 'Processing...' : 'Run Tool'}
                </button>
              </div>
            </div>
          )}

          {/* Result */}
          {currentResult && (
            <div className="glass p-8 animate-slide-up">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-sm font-semibold text-[var(--text-secondary)]">
                    Result — {currentResult.mode_used.toUpperCase()} mode
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  {(['txt', 'docx', 'pdf'] as const).map((f) => (
                    <button key={f} onClick={() => setExportFormat(f)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                        exportFormat === f ? 'bg-[var(--accent)]/15 text-[var(--accent-light)] border border-[var(--accent)]/20' : 'text-[var(--text-tertiary)] hover:text-white'
                      }`}>{f.toUpperCase()}</button>
                  ))}
                  <button onClick={handleExport} className="btn btn-secondary py-2 px-3 text-xs">
                    <Download size={14} /> Export
                  </button>
                </div>
              </div>
              <div className="bg-[var(--bg-input)] rounded-xl p-6 border border-[var(--border)]">
                <pre className="whitespace-pre-wrap text-sm leading-relaxed text-[var(--text-primary)]">
                  {currentResult.content}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
