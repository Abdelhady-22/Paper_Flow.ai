import { useState, useRef, useEffect, useCallback } from 'react';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import {
  addMessage, setSending, updateMessageFeedback, setSessions,
  setActiveSession, addSession, setMessages, setLoading,
} from '../store/slices/chatSlice';
import { setPapers, setActivePaper, setUploading, addPaper } from '../store/slices/paperSlice';
import api from '../api/client';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';
import {
  Send, Mic, MicOff, ThumbsUp, ThumbsDown, Copy, Volume2, Bot, User,
  Loader2, Plus, FileText, Upload, MessageSquare, Sparkles, PanelLeft,
  PanelLeftClose, Trash2
} from 'lucide-react';

const USER_ID = '00000000-0000-0000-0000-000000000001';

export default function ChatPage() {
  const dispatch = useAppDispatch();
  const { messages, activeSessionId, sending, loading, sessions } = useAppSelector((s) => s.chat);
  const { papers, activePaperId, uploading } = useAppSelector((s) => s.paper);
  const [input, setInput] = useState('');
  const [recording, setRecording] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => { loadPapers(); loadSessions(); }, []);
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

  const loadPapers = useCallback(async () => {
    try {
      const res = await api.get(`/ocr/papers?user_id=${USER_ID}`);
      dispatch(setPapers(res.data.data));
    } catch {}
  }, [dispatch]);

  const loadSessions = useCallback(async () => {
    try {
      const res = await api.get(`/chat/sessions?user_id=${USER_ID}`);
      dispatch(setSessions(res.data.data));
    } catch {}
  }, [dispatch]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    dispatch(setUploading(true));
    try {
      const res = await api.post(`/ocr/upload?user_id=${USER_ID}&engine=paddle&language=en`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      dispatch(addPaper(res.data.data));
      dispatch(setActivePaper(res.data.data.paper_id));
      toast.success('Paper uploaded!');
    } catch (err: any) { toast.error(err.message); }
    finally { dispatch(setUploading(false)); if (fileInputRef.current) fileInputRef.current.value = ''; }
  };

  const handleNewChat = async () => {
    try {
      const res = await api.post(`/chat/sessions?user_id=${USER_ID}`, { title: 'New Chat' });
      dispatch(addSession(res.data.data));
      dispatch(setActiveSession(res.data.data.session_id));
      dispatch(setMessages([]));
    } catch (err: any) { toast.error(err.message); }
  };

  const handleSelectSession = async (sessionId: string) => {
    dispatch(setActiveSession(sessionId));
    dispatch(setLoading(true));
    try {
      const res = await api.get(`/chat/sessions/${sessionId}/messages`);
      dispatch(setMessages(res.data.data));
    } catch {}
    dispatch(setLoading(false));
  };

  const sendMessage = async () => {
    if (!input.trim() || !activeSessionId) {
      if (!activeSessionId) toast.error('Create a chat first');
      return;
    }
    const content = input.trim();
    setInput('');
    dispatch(addMessage({ id: `temp-${Date.now()}`, role: 'user', content, input_type: 'text' }));
    dispatch(setSending(true));
    try {
      const res = await api.post(`/chat/message?user_id=${USER_ID}`, {
        content, session_id: activeSessionId, input_type: 'text',
      });
      dispatch(addMessage(res.data.data));
    } catch (err: any) { toast.error(err.message); }
    dispatch(setSending(false));
  };

  const handleVoice = async () => {
    if (recording) { mediaRecorderRef.current?.stop(); setRecording(false); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream);
      const chunks: Blob[] = [];
      mr.ondataavailable = (e) => chunks.push(e.data);
      mr.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const fd = new FormData();
        fd.append('file', blob, 'recording.webm');
        try {
          const r = await api.post('/voice/stt?provider=whisper&language=en', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
          setInput(r.data.data.text);
        } catch (err: any) { toast.error(err.message); }
      };
      mediaRecorderRef.current = mr;
      mr.start();
      setRecording(true);
    } catch { toast.error('Microphone access denied'); }
  };

  const handleFeedback = async (msgId: string, feedback: 'like' | 'dislike' | null) => {
    try {
      const ep = feedback === null ? `/chat/messages/${msgId}/remove-feedback` : `/chat/messages/${msgId}/${feedback}`;
      await api.patch(ep);
      dispatch(updateMessageFeedback({ id: msgId, feedback }));
    } catch {}
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied!');
  };

  const handleTTS = async (text: string) => {
    try {
      const r = await api.post('/voice/tts?text=' + encodeURIComponent(text.slice(0, 500)) + '&provider=edge_tts&language=en', null, { responseType: 'blob' });
      new Audio(URL.createObjectURL(r.data)).play();
    } catch (err: any) { toast.error(err.message); }
  };

  return (
    <div className="h-screen flex flex-col">
      <Navbar />
      <div className="flex flex-1 pt-16 overflow-hidden">
        {/* Sidebar */}
        <aside className={`transition-all duration-300 ${sidebarOpen ? 'w-72' : 'w-0'} overflow-hidden flex-shrink-0`}>
          <div className="w-72 h-full flex flex-col bg-[var(--bg-primary)] border-r border-[var(--border)]">
            {/* New Chat + Upload */}
            <div className="p-3 space-y-2">
              <button onClick={handleNewChat} className="btn btn-primary w-full" id="new-chat-btn">
                <Plus size={16} /> New Chat
              </button>
              <input ref={fileInputRef} type="file" accept=".pdf,.docx,.png,.jpg,.jpeg,.tiff,.bmp" onChange={handleUpload} className="hidden" id="file-upload" />
              <button onClick={() => fileInputRef.current?.click()} disabled={uploading} className="btn btn-secondary w-full" id="upload-btn">
                <Upload size={16} /> {uploading ? 'Uploading...' : 'Upload Paper'}
              </button>
            </div>

            {/* Papers */}
            <div className="px-3 mb-2">
              <h4 className="text-[10px] font-bold text-[var(--text-tertiary)] uppercase tracking-widest mb-2 px-1">Papers</h4>
              <div className="space-y-0.5 max-h-32 overflow-y-auto">
                {papers.length === 0 ? (
                  <p className="text-xs text-[var(--text-tertiary)] px-1 py-2">No papers yet</p>
                ) : papers.map((p) => (
                  <button key={p.paper_id} onClick={() => dispatch(setActivePaper(p.paper_id))}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs truncate transition-all ${
                      activePaperId === p.paper_id ? 'bg-[var(--accent)]/10 text-[var(--accent-light)] border border-[var(--accent)]/20' : 'text-[var(--text-secondary)] hover:bg-white/5'
                    }`}>
                    <FileText size={12} className="inline mr-1.5" />{p.filename}
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t border-[var(--border)] mx-3" />

            {/* Sessions */}
            <div className="flex-1 overflow-y-auto px-3 pt-2">
              <h4 className="text-[10px] font-bold text-[var(--text-tertiary)] uppercase tracking-widest mb-2 px-1">History</h4>
              <div className="space-y-0.5">
                {sessions.length === 0 ? (
                  <p className="text-xs text-[var(--text-tertiary)] px-1 py-2">No chats yet</p>
                ) : sessions.map((s) => (
                  <button key={s.session_id} onClick={() => handleSelectSession(s.session_id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-xs truncate transition-all ${
                      activeSessionId === s.session_id ? 'bg-[var(--accent)]/10 text-[var(--accent-light)] border border-[var(--accent)]/20' : 'text-[var(--text-secondary)] hover:bg-white/5'
                    }`}>
                    <MessageSquare size={12} className="inline mr-1.5" />{s.title}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Main Chat */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Toggle */}
          <div className="flex items-center gap-2 px-4 py-2 border-b border-[var(--border)]">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="btn-ghost p-2 rounded-lg" id="toggle-sidebar">
              {sidebarOpen ? <PanelLeftClose size={18} /> : <PanelLeft size={18} />}
            </button>
            <span className="text-sm text-[var(--text-secondary)]">
              {activePaperId ? '📄 Paper selected' : 'No paper selected'}
            </span>
          </div>

          {/* Messages */}
          {!activeSessionId ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center animate-fade-in max-w-lg">
                <div className="w-20 h-20 mx-auto mb-6 rounded-3xl bg-gradient-to-br from-[var(--accent)] to-[var(--cyan)] flex items-center justify-center animate-float">
                  <Bot size={36} className="text-white" />
                </div>
                <h2 className="text-3xl font-bold mb-3">Paper Flow AI</h2>
                <p className="text-[var(--text-secondary)] mb-6">
                  Upload a research paper and start an intelligent conversation with it.
                </p>
                <div className="grid grid-cols-2 gap-3 max-w-sm mx-auto">
                  {['Summarize this paper', 'What are the key findings?', 'Translate to Arabic', 'Generate study questions'].map((q, i) => (
                    <button key={i} className="card p-3 text-xs text-left text-[var(--text-secondary)] hover:text-white" onClick={() => { if (activeSessionId) { setInput(q); } }}>
                      <Sparkles size={12} className="text-[var(--accent)] mb-1" />
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 overflow-y-auto">
              <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
                {loading ? (
                  <div className="flex justify-center py-20"><Loader2 className="animate-spin text-[var(--accent)]" size={32} /></div>
                ) : messages.length === 0 ? (
                  <div className="text-center py-20 text-[var(--text-secondary)]">Send a message to start</div>
                ) : messages.map((msg, i) => (
                  <div key={msg.id || i} className="animate-fade-in" style={{ animationDelay: `${Math.min(i * 30, 300)}ms` }}>
                    <div className={`flex gap-4 ${msg.role === 'user' ? '' : ''}`}>
                      {/* Avatar */}
                      <div className={`w-8 h-8 rounded-xl flex-shrink-0 flex items-center justify-center ${
                        msg.role === 'assistant' ? 'bg-gradient-to-br from-[var(--accent)] to-[var(--cyan)]' : 'bg-[var(--bg-elevated)]'
                      }`}>
                        {msg.role === 'assistant' ? <Bot size={15} className="text-white" /> : <User size={15} className="text-[var(--text-secondary)]" />}
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-semibold text-[var(--text-tertiary)] mb-1.5">
                          {msg.role === 'assistant' ? 'Paper Flow AI' : 'You'}
                        </div>
                        <div className="text-sm leading-relaxed text-[var(--text-primary)] whitespace-pre-wrap">
                          {msg.content}
                        </div>

                        {/* Citations */}
                        {msg.citations && msg.citations.length > 0 && (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {msg.citations.map((c, ci) => (
                              <span key={ci} className="inline-flex items-center gap-1 text-[10px] px-2 py-1 rounded-md bg-[var(--accent)]/10 text-[var(--accent-light)] border border-[var(--accent)]/20">
                                <FileText size={10} />
                                {c.paper_title}{c.page_number ? ` p.${c.page_number}` : ''}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Actions */}
                        {msg.role === 'assistant' && (
                          <div className="flex items-center gap-0.5 mt-3">
                            {[
                              { icon: ThumbsUp, action: () => handleFeedback(msg.id, msg.feedback === 'like' ? null : 'like'), active: msg.feedback === 'like', color: 'text-emerald-400' },
                              { icon: ThumbsDown, action: () => handleFeedback(msg.id, msg.feedback === 'dislike' ? null : 'dislike'), active: msg.feedback === 'dislike', color: 'text-rose-400' },
                              { icon: Copy, action: () => handleCopy(msg.content), active: false, color: '' },
                              { icon: Volume2, action: () => handleTTS(msg.content), active: false, color: 'text-sky-400' },
                            ].map(({ icon: Icon, action, active, color }, ai) => (
                              <button key={ai} onClick={action} className={`p-1.5 rounded-lg transition-all ${active ? color : 'text-[var(--text-tertiary)] hover:text-[var(--text-primary)] hover:bg-white/5'}`}>
                                <Icon size={14} />
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                    {i < messages.length - 1 && <div className="border-t border-[var(--border)] mt-6" />}
                  </div>
                ))}
                <div ref={bottomRef} />
              </div>
            </div>
          )}

          {/* Input */}
          {activeSessionId && (
            <div className="p-4">
              <div className="max-w-3xl mx-auto">
                <div className="glass flex items-end gap-2 px-4 py-3">
                  <button onClick={handleVoice} className={`p-2.5 rounded-xl transition-all flex-shrink-0 ${recording ? 'bg-rose-500/20 text-rose-400 animate-pulse-glow' : 'text-[var(--text-tertiary)] hover:text-white hover:bg-white/5'}`} id="voice-input-btn">
                    {recording ? <MicOff size={18} /> : <Mic size={18} />}
                  </button>
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                    placeholder="Ask about your papers..."
                    rows={1}
                    className="flex-1 bg-transparent text-sm outline-none text-[var(--text-primary)] placeholder:text-[var(--text-tertiary)] resize-none max-h-32"
                    id="chat-input"
                    style={{ minHeight: '24px' }}
                  />
                  <button onClick={sendMessage} disabled={sending || !input.trim()} className={`p-2.5 rounded-xl transition-all flex-shrink-0 ${sending ? 'text-[var(--text-tertiary)]' : 'bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] shadow-md'}`} id="send-btn">
                    {sending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                  </button>
                </div>
                <p className="text-[10px] text-[var(--text-tertiary)] text-center mt-2">
                  Paper Flow AI may produce inaccurate information. Always verify with sources.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
