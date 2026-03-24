import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Array<{ paper_title: string; page_number?: number; section?: string }>;
  input_type?: 'text' | 'voice';
  feedback?: 'like' | 'dislike' | null;
  created_at?: string;
}

interface Session {
  session_id: string;
  title: string;
  created_at?: string;
  updated_at?: string;
}

interface ChatState {
  sessions: Session[];
  activeSessionId: string | null;
  messages: Message[];
  loading: boolean;
  sending: boolean;
}

const initialState: ChatState = {
  sessions: [],
  activeSessionId: null,
  messages: [],
  loading: false,
  sending: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setSessions: (state, action: PayloadAction<Session[]>) => {
      state.sessions = action.payload;
    },
    setActiveSession: (state, action: PayloadAction<string | null>) => {
      state.activeSessionId = action.payload;
    },
    setMessages: (state, action: PayloadAction<Message[]>) => {
      state.messages = action.payload;
    },
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
    },
    updateMessageFeedback: (state, action: PayloadAction<{ id: string; feedback: 'like' | 'dislike' | null }>) => {
      const msg = state.messages.find((m) => m.id === action.payload.id);
      if (msg) msg.feedback = action.payload.feedback;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setSending: (state, action: PayloadAction<boolean>) => {
      state.sending = action.payload;
    },
    addSession: (state, action: PayloadAction<Session>) => {
      state.sessions.unshift(action.payload);
    },
  },
});

export const { setSessions, setActiveSession, setMessages, addMessage, updateMessageFeedback, setLoading, setSending, addSession } = chatSlice.actions;
export default chatSlice.reducer;
