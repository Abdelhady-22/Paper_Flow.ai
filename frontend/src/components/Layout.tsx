import { useAppSelector, useAppDispatch } from '../store/hooks';
import { setActiveTab } from '../store/slices/uiSlice';
import Sidebar from './Sidebar';
import ChatPanel from './ChatPanel';
import ToolsPanel from './ToolsPanel';
import DiscoverPanel from './DiscoverPanel';
import { MessageSquare, Wrench, Search, PanelLeftClose, PanelLeft } from 'lucide-react';
import { toggleSidebar } from '../store/slices/uiSlice';

const tabs = [
  { key: 'chat' as const, label: 'Chat', icon: MessageSquare },
  { key: 'tools' as const, label: 'NLP Tools', icon: Wrench },
  { key: 'discover' as const, label: 'Discover', icon: Search },
];

export default function Layout() {
  const dispatch = useAppDispatch();
  const { sidebarOpen, activeTab } = useAppSelector((s) => s.ui);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <div
        className={`transition-all duration-300 ease-in-out ${
          sidebarOpen ? 'w-72' : 'w-0'
        } overflow-hidden`}
      >
        <Sidebar />
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="glass flex items-center justify-between px-4 py-3 border-b border-[var(--border)] z-10"
                style={{ borderRadius: 0 }}>
          <div className="flex items-center gap-3">
            <button
              onClick={() => dispatch(toggleSidebar())}
              className="btn-ghost p-2 rounded-lg"
              id="toggle-sidebar"
            >
              {sidebarOpen ? <PanelLeftClose size={20} /> : <PanelLeft size={20} />}
            </button>
            <h1 className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              Paper Flow AI
            </h1>
          </div>

          {/* Tabs */}
          <nav className="flex gap-1 bg-[var(--surface)] rounded-xl p-1">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                id={`tab-${tab.key}`}
                onClick={() => dispatch(setActiveTab(tab.key))}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  activeTab === tab.key
                    ? 'bg-gradient-to-r from-indigo-500/20 to-cyan-500/20 text-white border border-indigo-500/30'
                    : 'text-[var(--text-muted)] hover:text-white hover:bg-[var(--surface-2)]'
                }`}
              >
                <tab.icon size={16} />
                {tab.label}
              </button>
            ))}
          </nav>

          <div className="w-10" /> {/* Spacer for balance */}
        </header>

        {/* Content */}
        <main className="flex-1 overflow-hidden">
          {activeTab === 'chat' && <ChatPanel />}
          {activeTab === 'tools' && <ToolsPanel />}
          {activeTab === 'discover' && <DiscoverPanel />}
        </main>
      </div>
    </div>
  );
}
