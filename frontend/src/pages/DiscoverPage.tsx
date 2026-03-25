import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { staggerContainer, fadeInUp } from '../utils/motion';
import api from '../api/client';
import Navbar from '../components/Navbar';
import PageTransition from '../components/PageTransition';
import { Search, ArrowLeft, Loader, ExternalLink, Calendar, User } from 'lucide-react';

interface Paper {
  id: string;
  title: string;
  authors: string;
  year: string;
  abstract: string;
  url?: string;
}

export default function DiscoverPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', field: '', description: '' });
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    const query = `${form.name} ${form.field} ${form.description}`.trim();
    if (!query) return;
    setLoading(true);
    setHasSearched(true);
    try {
      const res = await api.post('/agent/search', {
        query: form.name || form.field,
        field: form.field,
        description: form.description,
      });
      const data = res.data;
      const results = data.papers || data.results || data;
      if (Array.isArray(results)) {
        setPapers(results.map((p: any, i: number) => ({
          id: p.id || p.paperId || String(i),
          title: p.title || 'Untitled',
          authors: p.authors || p.author || 'Unknown',
          year: p.year || p.publicationDate || '',
          abstract: p.abstract || p.summary || '',
          url: p.url || p.externalIds?.DOI || '',
        })));
      } else {
        setPapers([]);
      }
    } catch {
      setPapers([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <PageTransition>
        <div style={{ maxWidth: 900, margin: '0 auto', padding: '0 40px 40px' }}>
          <div className="tool-header">
            <button className="btn-ghost" onClick={() => navigate('/dashboard')}>
              <ArrowLeft size={16} /> Back
            </button>
            <div>
              <h1 className="gradient-text">Discover Papers</h1>
              <p className="header-subtitle">Search for research papers using AI-powered discovery</p>
            </div>
          </div>

          {/* Search Form */}
          <div style={{ width: '100%', marginTop: 32 }}>
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 8, color: 'var(--current-text-secondary)', fontSize: 14 }}>Paper Name (optional)</label>
              <input type="text" placeholder="e.g., Transformer architecture, BERT" value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                style={{
                  width: '100%', padding: '14px 16px', background: 'var(--current-surface)',
                  border: '1px solid var(--current-border)', borderRadius: 8,
                  color: 'var(--current-text-primary)', fontSize: 15, outline: 'none',
                  fontFamily: 'var(--font-primary)',
                }}
              />
            </div>
            <div style={{ marginBottom: 20 }}>
              <label style={{ display: 'block', marginBottom: 8, color: 'var(--current-text-secondary)', fontSize: 14 }}>Research Field</label>
              <input type="text" placeholder="e.g., Machine Learning, NLP, Computer Vision" value={form.field}
                onChange={e => setForm({ ...form, field: e.target.value })}
                style={{
                  width: '100%', padding: '14px 16px', background: 'var(--current-surface)',
                  border: '1px solid var(--current-border)', borderRadius: 8,
                  color: 'var(--current-text-primary)', fontSize: 15, outline: 'none',
                  fontFamily: 'var(--font-primary)',
                }}
              />
            </div>
            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', marginBottom: 8, color: 'var(--current-text-secondary)', fontSize: 14 }}>Description / Keywords</label>
              <textarea placeholder="Describe what you are looking for..." value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })} rows={4}
                style={{
                  width: '100%', padding: '14px 16px', background: 'var(--current-surface)',
                  border: '1px solid var(--current-border)', borderRadius: 8,
                  color: 'var(--current-text-primary)', fontSize: 15, resize: 'vertical',
                  outline: 'none', fontFamily: 'var(--font-primary)',
                }}
              />
            </div>
            <button className="btn btn-primary" style={{ width: '100%', padding: 16, fontSize: 16 }}
              onClick={handleSearch} disabled={loading || (!form.name && !form.field && !form.description)}
            >
              <Search size={20} />
              {loading ? 'Searching...' : 'Find Papers'}
            </button>
          </div>

          {/* Results */}
          {hasSearched && (
            <motion.div initial="hidden" animate="show" variants={staggerContainer} style={{ marginTop: 48 }}>
              <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 24 }}>
                Search Results {papers.length > 0 && <span style={{ color: 'var(--current-text-secondary)', fontWeight: 400 }}>({papers.length} found)</span>}
              </h3>
              {loading ? (
                <div style={{ textAlign: 'center', padding: 40 }}>
                  <Loader size={40} className="spin" style={{ color: 'var(--color-primary-cyan)' }} />
                  <p style={{ color: 'var(--current-text-secondary)', marginTop: 16 }}>Searching for papers...</p>
                </div>
              ) : papers.length > 0 ? (
                <div className="papers-grid">
                  {papers.map(paper => (
                    <motion.div key={paper.id} variants={fadeInUp} className="paper-entry-card"
                      whileHover={{ scale: 1.01 }}
                    >
                      <h4>{paper.title}</h4>
                      <div className="paper-meta">
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><User size={12} /> {paper.authors}</span>
                        <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}><Calendar size={12} /> {paper.year}</span>
                      </div>
                      <p className="paper-abstract">{paper.abstract}</p>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <p style={{ textAlign: 'center', opacity: 0.6, padding: 40 }}>No papers found. Try different keywords.</p>
              )}
            </motion.div>
          )}
        </div>
      </PageTransition>
    </>
  );
}
