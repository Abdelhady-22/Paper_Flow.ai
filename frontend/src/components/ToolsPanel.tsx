import { useState } from 'react';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { setSummaryResult, setTranslationResult, setQaResult, setProcessing } from '../store/slices/paperSlice';
import api from '../api/client';
import toast from 'react-hot-toast';
import { saveAs } from 'file-saver';
import {
  FileText, Languages, HelpCircle, Download, Loader2, BookOpen,
  ArrowRightLeft
} from 'lucide-react';

const USER_ID = '00000000-0000-0000-0000-000000000001';

export default function ToolsPanel() {
  const dispatch = useAppDispatch();
  const { activePaperId, processing, summaryResult, translationResult, qaResult } = useAppSelector((s) => s.paper);
  const [activeToolTab, setActiveToolTab] = useState<'summary' | 'translate' | 'qa'>('summary');
  const [summaryMode, setSummaryMode] = useState<'model' | 'llm'>('model');
  const [translateMode, setTranslateMode] = useState<'model' | 'llm'>('model');
  const [translateDir, setTranslateDir] = useState('en-ar');
  const [qaMode, setQaMode] = useState<'model' | 'llm'>('model');
  const [qaCount, setQaCount] = useState(5);
  const [exportFormat, setExportFormat] = useState<'txt' | 'docx' | 'pdf'>('pdf');

  const toolTabs = [
    { key: 'summary' as const, label: 'Summarize', icon: BookOpen },
    { key: 'translate' as const, label: 'Translate', icon: ArrowRightLeft },
    { key: 'qa' as const, label: 'Q&A', icon: HelpCircle },
  ];

  const handleSummarize = async () => {
    if (!activePaperId) return toast.error('Select a paper first');
    dispatch(setProcessing(true));
    try {
      const res = await api.post(`/summarize/?user_id=${USER_ID}`, {
        paper_id: activePaperId,
        mode: summaryMode,
      });
      dispatch(setSummaryResult(res.data.data));
      toast.success('Summary generated!');
    } catch (err: any) {
      toast.error(err.message || 'Summarization failed');
    }
    dispatch(setProcessing(false));
  };

  const handleTranslate = async () => {
    if (!activePaperId) return toast.error('Select a paper first');
    dispatch(setProcessing(true));
    try {
      const res = await api.post(`/translate/?user_id=${USER_ID}`, {
        paper_id: activePaperId,
        direction: translateDir,
        mode: translateMode,
      });
      dispatch(setTranslationResult(res.data.data));
      toast.success('Translation complete!');
    } catch (err: any) {
      toast.error(err.message || 'Translation failed');
    }
    dispatch(setProcessing(false));
  };

  const handleGenerateQA = async () => {
    if (!activePaperId) return toast.error('Select a paper first');
    dispatch(setProcessing(true));
    try {
      const res = await api.post(`/qa/generate?user_id=${USER_ID}`, {
        paper_id: activePaperId,
        mode: qaMode,
        num_questions: qaCount,
      });
      dispatch(setQaResult(res.data.data));
      toast.success('Q&A generated!');
    } catch (err: any) {
      toast.error(err.message || 'Q&A generation failed');
    }
    dispatch(setProcessing(false));
  };

  const handleExport = async () => {
    const result = activeToolTab === 'summary' ? summaryResult
      : activeToolTab === 'translate' ? translationResult
      : qaResult;
    if (!result) return toast.error('Generate a result first');

    try {
      const res = await api.post('/export/', {
        content: result.content,
        format: exportFormat,
        title: `${activeToolTab}_result`,
        language: translateDir === 'en-ar' ? 'ar' : 'en',
      }, { responseType: 'blob' });
      saveAs(new Blob([res.data]), `${activeToolTab}_result.${exportFormat}`);
      toast.success(`Exported as ${exportFormat.toUpperCase()}`);
    } catch (err: any) {
      toast.error(err.message || 'Export failed');
    }
  };

  const currentResult = activeToolTab === 'summary' ? summaryResult
    : activeToolTab === 'translate' ? translationResult
    : qaResult;

  return (
    <div className="flex h-full">
      {/* Tool Panel */}
      <div className="w-80 border-r border-[var(--border)] flex flex-col bg-[var(--surface)]">
        {/* Tool Tabs */}
        <div className="flex border-b border-[var(--border)]">
          {toolTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveToolTab(tab.key)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-all border-b-2 ${
                activeToolTab === tab.key
                  ? 'border-indigo-500 text-indigo-400'
                  : 'border-transparent text-[var(--text-muted)] hover:text-white'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tool Controls */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {!activePaperId && (
            <div className="glass p-4 text-center">
              <FileText size={24} className="mx-auto mb-2 text-[var(--text-muted)]" />
              <p className="text-sm text-[var(--text-muted)]">Select a paper from the sidebar</p>
            </div>
          )}

          {activePaperId && activeToolTab === 'summary' && (
            <div className="space-y-3 animate-fade-in">
              <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Mode</label>
              <div className="flex gap-2">
                {(['model', 'llm'] as const).map((m) => (
                  <button
                    key={m}
                    onClick={() => setSummaryMode(m)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      summaryMode === m
                        ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                        : 'bg-[var(--surface-2)] text-[var(--text-muted)] hover:text-white'
                    }`}
                  >{m.toUpperCase()}</button>
                ))}
              </div>
              <button
                onClick={handleSummarize}
                disabled={processing}
                className="btn btn-primary w-full justify-center"
              >
                {processing ? <Loader2 size={16} className="animate-spin" /> : <BookOpen size={16} />}
                {processing ? 'Summarizing...' : 'Summarize'}
              </button>
            </div>
          )}

          {activePaperId && activeToolTab === 'translate' && (
            <div className="space-y-3 animate-fade-in">
              <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Direction</label>
              <div className="flex gap-2">
                {[{ val: 'en-ar', label: 'EN → AR' }, { val: 'ar-en', label: 'AR → EN' }].map((d) => (
                  <button
                    key={d.val}
                    onClick={() => setTranslateDir(d.val)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      translateDir === d.val
                        ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                        : 'bg-[var(--surface-2)] text-[var(--text-muted)] hover:text-white'
                    }`}
                  >{d.label}</button>
                ))}
              </div>
              <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Mode</label>
              <div className="flex gap-2">
                {(['model', 'llm'] as const).map((m) => (
                  <button
                    key={m}
                    onClick={() => setTranslateMode(m)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      translateMode === m
                        ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                        : 'bg-[var(--surface-2)] text-[var(--text-muted)] hover:text-white'
                    }`}
                  >{m.toUpperCase()}</button>
                ))}
              </div>
              <button
                onClick={handleTranslate}
                disabled={processing}
                className="btn btn-primary w-full justify-center"
              >
                {processing ? <Loader2 size={16} className="animate-spin" /> : <Languages size={16} />}
                {processing ? 'Translating...' : 'Translate'}
              </button>
            </div>
          )}

          {activePaperId && activeToolTab === 'qa' && (
            <div className="space-y-3 animate-fade-in">
              <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Questions</label>
              <input
                type="number"
                min={1}
                max={20}
                value={qaCount}
                onChange={(e) => setQaCount(Number(e.target.value))}
                className="w-full bg-[var(--surface-2)] border border-[var(--border)] rounded-lg px-3 py-2 text-sm outline-none focus:border-indigo-500 transition-colors"
              />
              <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Mode</label>
              <div className="flex gap-2">
                {(['model', 'llm'] as const).map((m) => (
                  <button
                    key={m}
                    onClick={() => setQaMode(m)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      qaMode === m
                        ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
                        : 'bg-[var(--surface-2)] text-[var(--text-muted)] hover:text-white'
                    }`}
                  >{m.toUpperCase()}</button>
                ))}
              </div>
              <button
                onClick={handleGenerateQA}
                disabled={processing}
                className="btn btn-primary w-full justify-center"
              >
                {processing ? <Loader2 size={16} className="animate-spin" /> : <HelpCircle size={16} />}
                {processing ? 'Generating...' : 'Generate Q&A'}
              </button>
            </div>
          )}

          {/* Export */}
          {currentResult && (
            <div className="border-t border-[var(--border)] pt-4 space-y-3 animate-slide-up">
              <label className="block text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Export As</label>
              <div className="flex gap-2">
                {(['txt', 'docx', 'pdf'] as const).map((f) => (
                  <button
                    key={f}
                    onClick={() => setExportFormat(f)}
                    className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${
                      exportFormat === f
                        ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        : 'bg-[var(--surface-2)] text-[var(--text-muted)] hover:text-white'
                    }`}
                  >{f.toUpperCase()}</button>
                ))}
              </div>
              <button onClick={handleExport} className="btn btn-secondary w-full justify-center">
                <Download size={16} />
                Export
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Result Display */}
      <div className="flex-1 overflow-y-auto p-6">
        {currentResult ? (
          <div className="animate-slide-up">
            <div className="glass p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span className="text-xs text-[var(--text-muted)] uppercase tracking-wider font-semibold">
                  {activeToolTab} Result — {currentResult.mode_used} mode
                </span>
              </div>
              <div className="prose prose-invert prose-sm max-w-none">
                <pre className="whitespace-pre-wrap text-sm leading-relaxed text-[var(--text)]">
                  {currentResult.content}
                </pre>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center animate-fade-in">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 flex items-center justify-center border border-indigo-500/30">
                <FileText size={28} className="text-indigo-400" />
              </div>
              <h3 className="text-lg font-bold mb-1">NLP Tools</h3>
              <p className="text-sm text-[var(--text-muted)] max-w-sm">
                Select a paper, choose a tool, and click the action button to process it.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
