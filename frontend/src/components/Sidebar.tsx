import { useEffect, useCallback } from 'react';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { setPapers, setActivePaper, setUploading, addPaper } from '../store/slices/paperSlice';
import { setSessions, setActiveSession, addSession, setMessages, setLoading } from '../store/slices/chatSlice';
import api from '../api/client';
import toast from 'react-hot-toast';
import {
  FileText, Upload, Plus, MessageSquare, Trash2
} from 'lucide-react';
import { useRef } from 'react';

const USER_ID = '00000000-0000-0000-0000-000000000001'; // temp — no auth yet

export default function Sidebar() {
  const dispatch = useAppDispatch();
  const { papers, activePaperId, uploading } = useAppSelector((s) => s.paper);
  const { sessions, activeSessionId } = useAppSelector((s) => s.chat);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch papers and sessions on mount
  useEffect(() => {
    loadPapers();
    loadSessions();
  }, []);

  const loadPapers = useCallback(async () => {
    try {
      const res = await api.get(`/ocr/papers?user_id=${USER_ID}`);
      dispatch(setPapers(res.data.data));
    } catch { /* first load may fail */ }
  }, [dispatch]);

  const loadSessions = useCallback(async () => {
    try {
      const res = await api.get(`/chat/sessions?user_id=${USER_ID}`);
      dispatch(setSessions(res.data.data));
    } catch { /* first load may fail */ }
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
      toast.success('Paper uploaded successfully!');
    } catch (err: any) {
      toast.error(err.message || 'Upload failed');
    } finally {
      dispatch(setUploading(false));
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleNewChat = async () => {
    try {
      const res = await api.post(`/chat/sessions?user_id=${USER_ID}`, { title: 'New Chat' });
      dispatch(addSession(res.data.data));
      dispatch(setActiveSession(res.data.data.session_id));
      dispatch(setMessages([]));
    } catch (err: any) {
      toast.error(err.message || 'Failed to create session');
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    dispatch(setActiveSession(sessionId));
    dispatch(setLoading(true));
    try {
      const res = await api.get(`/chat/sessions/${sessionId}/messages`);
      dispatch(setMessages(res.data.data));
    } catch { /* ignore */ }
    dispatch(setLoading(false));
  };

  return (
    <aside className="h-full w-72 flex flex-col bg-[var(--surface)] border-r border-[var(--border)]">
      {/* Logo */}
      <div className="p-4 border-b border-[var(--border)]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center">
            <FileText size={20} className="text-white" />
          </div>
          <div>
            <h2 className="font-bold text-sm">Paper Flow AI</h2>
            <p className="text-xs text-[var(--text-muted)]">Research Assistant</p>
          </div>
        </div>
      </div>

      {/* Upload */}
      <div className="p-3">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.png,.jpg,.jpeg,.tiff,.bmp"
          onChange={handleUpload}
          className="hidden"
          id="file-upload"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="btn btn-primary w-full justify-center"
          id="upload-btn"
        >
          <Upload size={16} />
          {uploading ? 'Uploading...' : 'Upload Paper'}
        </button>
      </div>

      {/* Papers */}
      <div className="px-3 pb-2">
        <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-2">
          Papers
        </h3>
        <div className="space-y-1 max-h-40 overflow-y-auto">
          {papers.length === 0 ? (
            <p className="text-xs text-[var(--text-muted)] px-2 py-3">No papers yet</p>
          ) : (
            papers.map((p) => (
              <button
                key={p.paper_id}
                onClick={() => dispatch(setActivePaper(p.paper_id))}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition-all ${
                  activePaperId === p.paper_id
                    ? 'bg-indigo-500/20 text-white border border-indigo-500/30'
                    : 'text-[var(--text-muted)] hover:bg-[var(--surface-2)] hover:text-white'
                }`}
              >
                <FileText size={14} className="inline mr-2" />
                {p.filename}
              </button>
            ))
          )}
        </div>
      </div>

      <div className="border-t border-[var(--border)] mx-3" />

      {/* Chat Sessions */}
      <div className="flex-1 flex flex-col overflow-hidden px-3 pt-2">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
            Chats
          </h3>
          <button onClick={handleNewChat} className="btn-ghost p-1 rounded-lg" id="new-chat-btn">
            <Plus size={16} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto space-y-1">
          {sessions.length === 0 ? (
            <p className="text-xs text-[var(--text-muted)] px-2 py-3">No chats yet</p>
          ) : (
            sessions.map((s) => (
              <button
                key={s.session_id}
                onClick={() => handleSelectSession(s.session_id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition-all ${
                  activeSessionId === s.session_id
                    ? 'bg-indigo-500/20 text-white border border-indigo-500/30'
                    : 'text-[var(--text-muted)] hover:bg-[var(--surface-2)] hover:text-white'
                }`}
              >
                <MessageSquare size={14} className="inline mr-2" />
                {s.title}
              </button>
            ))
          )}
        </div>
      </div>
    </aside>
  );
}
