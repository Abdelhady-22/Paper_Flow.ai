import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { staggerContainer, fadeInUp } from '../utils/motion';
import api from '../api/client';
import {
  FileText, Paperclip, Mic, Send, Copy, ThumbsUp, ThumbsDown,
  Home, MoreVertical, Trash2, Download, BookOpen, Bot, ArrowLeft,
  Sparkles, Search, HelpCircle, Globe
} from 'lucide-react';

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
  timestamp: string;
}

const suggestedPrompts = [
  { icon: <FileText size={20} />, text: 'Summarize my uploaded paper' },
  { icon: <Search size={20} />, text: 'Find related research on this topic' },
  { icon: <HelpCircle size={20} />, text: 'Generate questions from this paper' },
  { icon: <Globe size={20} />, text: 'Translate the abstract to Arabic' },
  { icon: <Sparkles size={20} />, text: 'What are the key findings?' },
];

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const [reactions, setReactions] = useState<Record<number, string>>({});
  const messagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesRef.current?.scrollTo({ top: messagesRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, isTyping]);

  const handleSend = async (text: string = input) => {
    if (!text.trim()) return;
    const userMsg: Message = { id: Date.now(), text, sender: 'user', timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await api.post('/chat/message', { message: text });
      setIsTyping(false);
      const botMsg: Message = {
        id: Date.now() + 1,
        text: res.data.response || res.data.answer || JSON.stringify(res.data),
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, botMsg]);
    } catch {
      setIsTyping(false);
      const botMsg: Message = {
        id: Date.now() + 1,
        text: `I received your message: "${text}". The backend is currently unavailable — please ensure the gateway is running on port 8000.`,
        sender: 'bot',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, botMsg]);
    }
  };

  const formatTime = (ts: string) => new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const isEmpty = messages.length === 0 && !isTyping;

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 24px', height: 64, borderBottom: '1px solid var(--current-border)',
        background: 'var(--current-card-bg)', backdropFilter: 'blur(10px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <button className="btn-ghost" onClick={() => navigate('/dashboard')} style={{ padding: 8 }}>
            <ArrowLeft size={20} />
          </button>
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>
              {messages.length > 0 ? messages[0].text.substring(0, 40) + '...' : 'Paper Flow Chat'}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--current-text-secondary)' }}>
              <Bot size={12} /> <span>AI Ready</span>
              <span>•</span>
              <span style={{ color: 'var(--color-success)' }}>✓ Connected</span>
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button className="btn-ghost" onClick={() => navigate('/dashboard')} style={{ padding: 8 }}><Home size={18} /></button>
          <div style={{ position: 'relative' }}>
            <button className="btn-ghost" onClick={() => setShowActions(!showActions)} style={{ padding: 8 }}><MoreVertical size={18} /></button>
            {showActions && (
              <div style={{
                position: 'absolute', right: 0, top: '100%', marginTop: 8,
                background: 'var(--current-card-bg)', border: '1px solid var(--current-border)',
                borderRadius: 12, padding: 8, minWidth: 180, zIndex: 50,
                boxShadow: 'var(--shadow-lg)',
              }}>
                <button onClick={() => { setMessages([]); setShowActions(false); }} style={{
                  display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '10px 12px',
                  background: 'transparent', border: 'none', color: 'var(--current-text-primary)',
                  borderRadius: 8, cursor: 'pointer', fontSize: 14,
                }}><Trash2 size={16} /> Clear Chat</button>
                <button style={{
                  display: 'flex', alignItems: 'center', gap: 8, width: '100%', padding: '10px 12px',
                  background: 'transparent', border: 'none', color: 'var(--current-text-primary)',
                  borderRadius: 8, cursor: 'pointer', fontSize: 14,
                }}><Download size={16} /> Export</button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={messagesRef} style={{ flex: 1, overflowY: 'auto', padding: 24 }}>
        {isEmpty ? (
          <motion.div initial="hidden" animate="show" variants={staggerContainer}
            style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', textAlign: 'center' }}
          >
            <motion.div variants={fadeInUp}>
              <div style={{
                width: 72, height: 72, borderRadius: '50%', background: 'rgba(0,212,255,0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px',
              }}>
                <Sparkles size={32} color="var(--color-primary-cyan)" />
              </div>
            </motion.div>
            <motion.h2 variants={fadeInUp} style={{ fontSize: 24, fontWeight: 700, marginBottom: 8 }}>
              How can I help you today?
            </motion.h2>
            <motion.p variants={fadeInUp} style={{ color: 'var(--current-text-secondary)', marginBottom: 32, maxWidth: 400 }}>
              Ask me about your research papers, summarize content, translate, or generate questions.
            </motion.p>
            <motion.div variants={fadeInUp} style={{ display: 'flex', flexWrap: 'wrap', gap: 12, justifyContent: 'center', maxWidth: 600 }}>
              {suggestedPrompts.map((p, i) => (
                <motion.button key={i} whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                  onClick={() => handleSend(p.text)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 8, padding: '12px 18px',
                    background: 'var(--current-card-bg)', border: '1px solid var(--current-border)',
                    borderRadius: 12, cursor: 'pointer', color: 'var(--current-text-primary)',
                    fontSize: 14, transition: 'all 0.2s',
                  }}
                >
                  <span style={{ color: 'var(--color-primary-cyan)' }}>{p.icon}</span>
                  {p.text}
                </motion.button>
              ))}
            </motion.div>
          </motion.div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            {messages.map(msg => (
              <div key={msg.id} className={`chat-bubble-row ${msg.sender}`}>
                {msg.sender === 'bot' && (
                  <div className="avatar-bot"><Sparkles size={18} /></div>
                )}
                <div>
                  <div className="chat-bubble-content">
                    <p style={{ margin: 0 }}>{msg.text}</p>
                  </div>
                  <div className="message-actions">
                    <button className="action-btn" onClick={() => navigator.clipboard.writeText(msg.text)}><Copy size={14} /></button>
                    {msg.sender === 'bot' && (
                      <>
                        <button className={`action-btn ${reactions[msg.id] === 'liked' ? 'active' : ''}`}
                          onClick={() => setReactions(prev => ({ ...prev, [msg.id]: prev[msg.id] === 'liked' ? '' : 'liked' }))}
                        ><ThumbsUp size={14} /></button>
                        <button className={`action-btn ${reactions[msg.id] === 'disliked' ? 'active' : ''}`}
                          onClick={() => setReactions(prev => ({ ...prev, [msg.id]: prev[msg.id] === 'disliked' ? '' : 'disliked' }))}
                        ><ThumbsDown size={14} /></button>
                      </>
                    )}
                    <span style={{ fontSize: 11, color: 'var(--current-text-secondary)', marginLeft: 8 }}>{formatTime(msg.timestamp)}</span>
                  </div>
                </div>
                {msg.sender === 'user' && (
                  <div className="avatar-user">U</div>
                )}
              </div>
            ))}
            {isTyping && (
              <div className="chat-bubble-row bot">
                <div className="avatar-bot"><Sparkles size={18} /></div>
                <div className="chat-bubble-content typing-indicator">
                  <span /><span /><span />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="chat-input-bar">
        <button className="btn-chat-action"><Paperclip size={18} /></button>
        <button className="btn-chat-action"><Mic size={18} /></button>
        <input
          type="text"
          placeholder="Ask about your research papers..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
        />
        <button className="btn-send-chat" onClick={() => handleSend()} disabled={!input.trim()}>
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
