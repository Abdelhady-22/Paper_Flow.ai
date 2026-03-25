import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import {
  Home, MessageCircle, FileText, Settings, Sun, Moon, LogOut
} from 'lucide-react';

export default function Navbar() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const { theme, changeTheme } = useTheme();

  const isActive = (path: string) => pathname === path ? 'active' : '';

  return (
    <nav style={{
      background: 'var(--current-card-bg)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--current-border)',
      padding: '0 40px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      height: '72px',
      transition: 'all 0.3s ease',
    }}>
      {/* Left: Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => navigate('/')}>
        <div style={{
          width: 36, height: 36, borderRadius: 10,
          background: 'linear-gradient(135deg, #00D4FF, #00A8CC)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <FileText size={18} color="#fff" />
        </div>
        <span style={{ fontSize: 18, fontWeight: 700, letterSpacing: -0.5 }} className="gradient-text">Paper Flow AI</span>
      </div>

      {/* Center: Links */}
      <ul style={{
        display: 'flex', gap: 32, listStyle: 'none', margin: 0, padding: 0, alignItems: 'center',
      }}>
        {[
          { to: '/dashboard', label: 'Dashboard', icon: Home },
          { to: '/chat', label: 'Chat', icon: MessageCircle },
          { to: '/research', label: 'Research', icon: FileText },
        ].map(link => (
          <li key={link.to}>
            <Link to={link.to} className={`${isActive(link.to)}`} style={{
              color: pathname === link.to ? 'var(--color-primary-cyan)' : 'var(--current-text-secondary)',
              textDecoration: 'none', fontWeight: 500, fontSize: 15,
              padding: '8px 0',
              borderBottom: pathname === link.to ? '2px solid var(--color-primary-cyan)' : '2px solid transparent',
              transition: 'all 0.3s ease',
              display: 'flex', alignItems: 'center', gap: 8,
            }}>
              <link.icon size={18} />
              {link.label}
            </Link>
          </li>
        ))}
      </ul>

      {/* Right: Theme + Avatar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <button onClick={() => changeTheme(theme === 'dark' ? 'light' : 'dark')}
          style={{
            background: 'transparent', border: '1px solid var(--current-border)',
            color: 'var(--current-text-secondary)', padding: 8, borderRadius: 8,
            cursor: 'pointer', display: 'flex', alignItems: 'center', transition: 'all 0.3s',
          }}
          title={theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div style={{
          width: 1, height: 24, background: 'var(--current-border)',
        }} />
        <div style={{
          width: 36, height: 36, borderRadius: '50%',
          background: 'linear-gradient(135deg, #00D4FF, #0A1628)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#fff', fontWeight: 600, fontSize: 13, cursor: 'pointer',
        }} onClick={() => navigate('/dashboard')}>
          U
        </div>
      </div>
    </nav>
  );
}
