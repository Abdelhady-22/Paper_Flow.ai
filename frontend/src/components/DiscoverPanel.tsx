import { useState, useEffect, useRef } from 'react';
import api from '../api/client';
import toast from 'react-hot-toast';
import { Search, Download, Globe, Loader2, BookOpen, ExternalLink } from 'lucide-react';

const USER_ID = '00000000-0000-0000-0000-000000000001';

interface SearchResult {
  title: string;
  authors: string[];
  year: number;
  abstract: string;
  pdf_url?: string;
  citation_count?: number;
}

export default function DiscoverPanel() {
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [searching, setSearching] = useState(false);
  const [discovering, setDiscovering] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [progress, setProgress] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);

  // WebSocket for progress
  useEffect(() => {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/progress`;
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        setProgress(data.message || '');
      } catch { /* ignore */ }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setResults([]);
    try {
      const res = await api.post('/agent/search', {
        query: query.trim(),
        max_results: maxResults,
      });
      setResults(res.data.data.papers || []);
      if (res.data.data.papers?.length === 0) toast('No papers found');
    } catch (err: any) {
      toast.error(err.message || 'Search failed');
    }
    setSearching(false);
  };

  const handleDiscover = async () => {
    if (!query.trim()) return;
    setDiscovering(true);
    setProgress('Starting discovery pipeline...');
    try {
      const res = await api.post(`/agent/discover?user_id=${USER_ID}`, {
        query: query.trim(),
        max_papers: maxResults,
        auto_import: true,
      });
      toast.success(`Discovery complete! ${res.data.data.papers_imported || 0} papers imported.`);
      setProgress('');
    } catch (err: any) {
      toast.error(err.message || 'Discovery failed');
    }
    setDiscovering(false);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Search Header */}
      <div className="p-6 border-b border-[var(--border)]">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Globe size={22} className="text-cyan-400" />
            Paper Discovery
          </h2>
          <div className="glass flex items-center gap-2 px-4 py-3">
            <Search size={18} className="text-[var(--text-muted)]" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search research papers on Semantic Scholar..."
              className="flex-1 bg-transparent text-sm outline-none text-[var(--text)] placeholder:text-[var(--text-muted)]"
              id="discover-input"
            />
            <div className="flex items-center gap-2">
              <select
                value={maxResults}
                onChange={(e) => setMaxResults(Number(e.target.value))}
                className="bg-[var(--surface-2)] text-sm rounded-lg px-2 py-1 text-[var(--text)] outline-none border border-[var(--border)]"
              >
                {[5, 10, 20, 50].map((n) => (
                  <option key={n} value={n}>{n} results</option>
                ))}
              </select>
              <button
                onClick={handleSearch}
                disabled={searching || !query.trim()}
                className="btn btn-primary py-2"
                id="search-btn"
              >
                {searching ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
                Search
              </button>
              <button
                onClick={handleDiscover}
                disabled={discovering || !query.trim()}
                className="btn py-2"
                style={{ background: 'linear-gradient(135deg, #0ea5e9, #6366f1)', color: 'white' }}
                id="discover-btn"
              >
                {discovering ? <Loader2 size={16} className="animate-spin" /> : <Download size={16} />}
                Full Pipeline
              </button>
            </div>
          </div>

          {/* Progress */}
          {discovering && progress && (
            <div className="mt-3 glass px-4 py-2 flex items-center gap-2 animate-fade-in">
              <Loader2 size={14} className="animate-spin text-cyan-400" />
              <span className="text-sm text-cyan-400">{progress}</span>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto space-y-3">
          {results.length === 0 && !searching && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center animate-fade-in">
                <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-indigo-500/20 flex items-center justify-center border border-cyan-500/30">
                  <Search size={28} className="text-cyan-400" />
                </div>
                <h3 className="text-lg font-bold mb-1">Discover Papers</h3>
                <p className="text-sm text-[var(--text-muted)] max-w-sm">
                  Search for papers or run the full AI-powered discovery pipeline
                  to find, download, and import papers automatically.
                </p>
              </div>
            </div>
          )}

          {results.map((paper, i) => (
            <div key={i} className="glass p-4 hover:border-indigo-500/30 transition-all animate-slide-up" style={{ animationDelay: `${i * 50}ms` }}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm leading-snug mb-1">{paper.title}</h3>
                  <p className="text-xs text-[var(--text-muted)] mb-2">
                    {paper.authors?.slice(0, 3).join(', ')}
                    {paper.authors?.length > 3 ? ' et al.' : ''}
                    {paper.year ? ` · ${paper.year}` : ''}
                    {paper.citation_count ? ` · ${paper.citation_count} citations` : ''}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] line-clamp-3">{paper.abstract}</p>
                </div>
                {paper.pdf_url && (
                  <a
                    href={paper.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-ghost p-2 rounded-lg flex-shrink-0"
                  >
                    <ExternalLink size={16} />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
