import { Link, useLocation } from 'react-router-dom';
import {
  FileText, MessageSquare, Wrench, Search, Sparkles
} from 'lucide-react';

const navLinks = [
  { to: '/', label: 'Home', icon: Sparkles },
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/tools', label: 'NLP Tools', icon: Wrench },
  { to: '/discover', label: 'Discover', icon: Search },
];

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-strong" style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}>
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[var(--accent)] to-[var(--cyan)] flex items-center justify-center shadow-lg group-hover:shadow-[0_0_20px_var(--accent-glow)] transition-shadow">
            <FileText size={18} className="text-white" />
          </div>
          <span className="text-lg font-bold gradient-text">Paper Flow AI</span>
        </Link>

        {/* Nav Links */}
        <div className="flex items-center gap-1 bg-[var(--bg-input)] rounded-xl p-1 border border-[var(--border)]">
          {navLinks.map((link) => {
            const isActive = pathname === link.to;
            return (
              <Link
                key={link.to}
                to={link.to}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-[var(--accent)] text-white shadow-md'
                    : 'text-[var(--text-secondary)] hover:text-white hover:bg-white/5'
                }`}
              >
                <link.icon size={15} />
                {link.label}
              </Link>
            );
          })}
        </div>

        <div className="w-9" />
      </div>
    </nav>
  );
}
