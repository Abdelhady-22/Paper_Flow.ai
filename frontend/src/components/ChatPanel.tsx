import { useState, useRef, useEffect } from 'react';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { addMessage, setSending, updateMessageFeedback } from '../store/slices/chatSlice';
import api from '../api/client';
import toast from 'react-hot-toast';
import {
  Send, Mic, MicOff, ThumbsUp, ThumbsDown, Copy, Volume2, Bot, User,
  Loader2
} from 'lucide-react';

const USER_ID = '00000000-0000-0000-0000-000000000001';

export default function ChatPanel() {
  const dispatch = useAppDispatch();
  const { messages, activeSessionId, sending, loading } = useAppSelector((s) => s.chat);
  const [input, setInput] = useState('');
  const [recording, setRecording] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || !activeSessionId) {
      if (!activeSessionId) toast.error('Create or select a chat first');
      return;
    }

    const content = input.trim();
    setInput('');

    // Optimistic user message
    dispatch(addMessage({
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      input_type: 'text',
    }));

    dispatch(setSending(true));
    try {
      const res = await api.post(`/chat/message?user_id=${USER_ID}`, {
        content,
        session_id: activeSessionId,
        input_type: 'text',
      });
      dispatch(addMessage(res.data.data));
    } catch (err: any) {
      toast.error(err.message || 'Failed to send message');
    }
    dispatch(setSending(false));
  };

  const handleVoiceInput = async () => {
    if (recording) {
      mediaRecorderRef.current?.stop();
      setRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', blob, 'recording.webm');

        try {
          const res = await api.post('/voice/stt?provider=whisper&language=en', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          setInput(res.data.data.text);
        } catch (err: any) {
          toast.error(err.message || 'Transcription failed');
        }
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setRecording(true);
    } catch {
      toast.error('Microphone access denied');
    }
  };

  const handleFeedback = async (msgId: string, feedback: 'like' | 'dislike' | null) => {
    try {
      const endpoint = feedback === null
        ? `/chat/messages/${msgId}/remove-feedback`
        : `/chat/messages/${msgId}/${feedback}`;
      await api.patch(endpoint);
      dispatch(updateMessageFeedback({ id: msgId, feedback }));
    } catch { /* ignore */ }
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  const handleTTS = async (text: string) => {
    try {
      const res = await api.post('/voice/tts?text=' + encodeURIComponent(text.slice(0, 500)) + '&provider=edge_tts&language=en', null, { responseType: 'blob' });
      const url = URL.createObjectURL(res.data);
      const audio = new Audio(url);
      audio.play();
    } catch (err: any) {
      toast.error(err.message || 'TTS failed');
    }
  };

  if (!activeSessionId) {
    return (
      <div className="flex-1 flex items-center justify-center h-full">
        <div className="text-center animate-fade-in">
          <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 flex items-center justify-center border border-indigo-500/30">
            <Bot size={36} className="text-indigo-400" />
          </div>
          <h2 className="text-2xl font-bold mb-2">Welcome to Paper Flow AI</h2>
          <p className="text-[var(--text-muted)] max-w-md">
            Upload a research paper and start chatting with it.
            Create a new chat session from the sidebar to begin.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="animate-spin text-indigo-400" size={32} />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-[var(--text-muted)]">
            Send a message to start the conversation
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={msg.id || i}
              className={`flex gap-3 animate-fade-in ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex-shrink-0 flex items-center justify-center">
                  <Bot size={16} className="text-white" />
                </div>
              )}
              <div
                className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white'
                    : 'glass'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>

                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-white/10">
                    <p className="text-xs text-[var(--text-muted)] font-medium mb-1">Sources:</p>
                    {msg.citations.map((c, ci) => (
                      <p key={ci} className="text-xs text-[var(--text-muted)]">
                        [{ci + 1}] {c.paper_title}{c.page_number ? `, p.${c.page_number}` : ''}
                      </p>
                    ))}
                  </div>
                )}

                {/* Actions (assistant only) */}
                {msg.role === 'assistant' && (
                  <div className="flex items-center gap-1 mt-2 pt-2 border-t border-white/10">
                    <button
                      onClick={() => handleFeedback(msg.id, msg.feedback === 'like' ? null : 'like')}
                      className={`p-1 rounded transition-colors ${
                        msg.feedback === 'like' ? 'text-green-400' : 'text-[var(--text-muted)] hover:text-green-400'
                      }`}
                    ><ThumbsUp size={14} /></button>
                    <button
                      onClick={() => handleFeedback(msg.id, msg.feedback === 'dislike' ? null : 'dislike')}
                      className={`p-1 rounded transition-colors ${
                        msg.feedback === 'dislike' ? 'text-red-400' : 'text-[var(--text-muted)] hover:text-red-400'
                      }`}
                    ><ThumbsDown size={14} /></button>
                    <button
                      onClick={() => handleCopy(msg.content)}
                      className="p-1 rounded text-[var(--text-muted)] hover:text-white transition-colors"
                    ><Copy size={14} /></button>
                    <button
                      onClick={() => handleTTS(msg.content)}
                      className="p-1 rounded text-[var(--text-muted)] hover:text-cyan-400 transition-colors"
                    ><Volume2 size={14} /></button>
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-[var(--surface-3)] flex-shrink-0 flex items-center justify-center">
                  <User size={16} className="text-[var(--text-muted)]" />
                </div>
              )}
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-[var(--border)]">
        <div className="glass flex items-center gap-2 px-4 py-2">
          <button
            onClick={handleVoiceInput}
            className={`p-2 rounded-lg transition-all ${
              recording
                ? 'bg-red-500/20 text-red-400 animate-pulse-glow'
                : 'text-[var(--text-muted)] hover:text-white hover:bg-[var(--surface-3)]'
            }`}
            id="voice-input-btn"
          >
            {recording ? <MicOff size={18} /> : <Mic size={18} />}
          </button>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Ask about your papers..."
            className="flex-1 bg-transparent text-sm outline-none text-[var(--text)] placeholder:text-[var(--text-muted)]"
            id="chat-input"
          />
          <button
            onClick={sendMessage}
            disabled={sending || !input.trim()}
            className={`p-2 rounded-lg transition-all ${
              sending
                ? 'text-[var(--text-muted)]'
                : 'text-indigo-400 hover:bg-indigo-500/20'
            }`}
            id="send-btn"
          >
            {sending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </div>
      </div>
    </div>
  );
}
