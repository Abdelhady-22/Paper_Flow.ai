import { useState, useEffect, useRef } from 'react';
import api from '../api/client';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';
import {
  Search, Globe, Loader2, ExternalLink, Download, BookOpen, Users,
  Calendar, Quote, Sparkles, ArrowRight, Zap
} from 'lucide-react';

const USER_ID = '00000000-0000-0000-0000-000000000001';

interface Paper {
  title: string;
  authors: string[];
  year: number;
  abstract: string;
  pdf_url?: string;
  citation_count?: number;
}

export default function DiscoverPage() {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [searching, setSearching] = useState(false);
  const [discovering, setDiscovering] = useState(false);
  const [results, setResults] = useState<Paper[]>([]);
  const [progress, setProgress] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    try {
      const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss:' : 'ws:'}//${location.host}/ws/progress`);
      ws.onmessage = (e) => { try { setProgress(JSON.parse(e.data).message || ''); } catch {} };
      wsRef.current = ws;
      return () => ws.close();
    } catch {}
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setResults([]);
    try {
      const res = await api.post('/agent/search', { query: query.trim(), max_results: maxResults });
      setResults(res.data.data.papers || []);
      if (!res.data.data.papers?.length) toast('No papers found');
    } catch (err: any) { toast.error(err.message); }
    setSearching(false);
  };

  const handleDiscover = async () => {
    if (!query.trim()) return;
    setDiscovering(true);
    setProgress('Starting discovery pipeline...');
    try {
      const res = await api.post(`/agent/discover?user_id=${USER_ID}`, { query: query.trim(), max_papers: maxResults, auto_import: true });
      toast.success(`Done! ${res.data.data.papers_imported || 0} papers imported.`);
      setProgress('');
    } catch (err: any) { toast.error(err.message); }
    setDiscovering(false);
  };

  return (
    <div className="min-h-screen relative">
      <Navbar />

      {/* Orb */}
      <div className="orb w-[400px] h-[400px] bg-[var(--cyan)] top-[60px] right-[-100px]" />

      <div className="pt-24 pb-16 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-10 animate-fade-in-down">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--cyan)]/10 border border-[var(--cyan)]/20 text-[var(--cyan)] text-sm font-medium mb-6">
              <Globe size={14} />
              Semantic Scholar Integration
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              Discover <span className="gradient-text">New Papers</span>
            </h1>
            <p className="text-[var(--text-secondary)] max-w-lg mx-auto">
              Search millions of academic papers or run the full AI pipeline to
              discover, download, and import papers automatically.
            </p>
          </div>

          {/* Search Box */}
          <div className="glass p-6 mb-8 animate-slide-up">
            <div className="flex items-center gap-3 bg-[var(--bg-input)] rounded-xl px-4 py-3 border border-[var(--border)] focus-within:border-[var(--accent)] transition-colors mb-4">
              <Search size={18} className="text-[var(--text-tertiary)] flex-shrink-0" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Search for research papers..."
                className="flex-1 bg-transparent text-sm outline-none text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)]"
                id="discover-input"
              />
            </div>

            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <label className="text-xs text-[var(--text-tertiary)]">Results:</label>
                <select value={maxResults} onChange={(e) => setMaxResults(Number(e.target.value))}
                  className="bg-[var(--bg-input)] text-sm rounded-lg px-3 py-1.5 text-[var(--text-primary)] outline-none border border-[var(--border)]">
                  {[5, 10, 20, 50].map((n) => <option key={n} value={n}>{n}</option>)}
                </select>
              </div>

              <div className="flex items-center gap-3">
                <button onClick={handleSearch} disabled={searching || !query.trim()} className="btn btn-secondary" id="search-btn">
                  {searching ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                  Quick Search
                </button>
                <button onClick={handleDiscover} disabled={discovering || !query.trim()} className="btn btn-primary" id="discover-btn"
                  style={{ background: 'linear-gradient(135deg, #22d3ee, #7c5cff)' }}>
                  {discovering ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
                  Full AI Pipeline
                </button>
              </div>
            </div>

            {/* Progress */}
            {discovering && progress && (
              <div className="mt-4 flex items-center gap-3 px-4 py-3 rounded-xl bg-[var(--cyan)]/10 border border-[var(--cyan)]/20 animate-fade-in">
                <Loader2 size={14} className="animate-spin text-[var(--cyan)]" />
                <span className="text-sm text-[var(--cyan)]">{progress}</span>
              </div>
            )}
          </div>

          {/* Results */}
          {results.length === 0 && !searching ? (
            <div className="text-center py-20 animate-fade-in">
              <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-[var(--cyan)]/20 to-[var(--accent)]/20 flex items-center justify-center border border-[var(--cyan)]/20 animate-float">
                <BookOpen size={32} className="text-[var(--cyan)]" />
              </div>
              <h3 className="text-xl font-bold mb-2">Start Exploring</h3>
              <p className="text-sm text-[var(--text-secondary)] max-w-md mx-auto mb-6">
                Enter a research topic above to search Semantic Scholar's database
                of over 200 million papers.
              </p>
              <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
                {['transformer architecture', 'natural language processing', 'computer vision 2024', 'reinforcement learning'].map((q) => (
                  <button key={q} onClick={() => { setQuery(q); }} className="px-3 py-1.5 rounded-lg text-xs bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-secondary)] hover:text-white hover:border-[var(--border-hover)] transition-all">
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {searching && (
                <div className="flex justify-center py-10"><Loader2 className="animate-spin text-[var(--accent)]" size={32} /></div>
              )}
              {results.map((paper, i) => (
                <div key={i} className="card p-5 animate-slide-up" style={{ animationDelay: `${i * 60}ms` }}>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-[15px] leading-snug mb-2 text-[var(--text-primary)]">
                        {paper.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-3 text-xs text-[var(--text-secondary)] mb-3">
                        {paper.authors?.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Users size={12} />
                            {paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ' et al.' : ''}
                          </span>
                        )}
                        {paper.year && (
                          <span className="flex items-center gap-1">
                            <Calendar size={12} /> {paper.year}
                          </span>
                        )}
                        {paper.citation_count ? (
                          <span className="flex items-center gap-1 text-[var(--amber)]">
                            <Quote size={12} /> {paper.citation_count} citations
                          </span>
                        ) : null}
                      </div>
                      <p className="text-xs text-[var(--text-tertiary)] leading-relaxed line-clamp-3">
                        {paper.abstract}
                      </p>
                    </div>
                    {paper.pdf_url && (
                      <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer"
                        className="btn btn-ghost p-2 rounded-xl flex-shrink-0 text-[var(--text-tertiary)] hover:text-[var(--accent)]">
                        <ExternalLink size={18} />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
