import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Paper {
  paper_id: string;
  filename: string;
  status: string;
  language: string;
  source: string;
  page_count?: number;
  created_at?: string;
}

interface ToolResult {
  content: string;
  mode_used: string;
  created_at?: string;
}

interface PaperState {
  papers: Paper[];
  activePaperId: string | null;
  uploading: boolean;
  processing: boolean;
  summaryResult: ToolResult | null;
  translationResult: ToolResult | null;
  qaResult: ToolResult | null;
}

const initialState: PaperState = {
  papers: [],
  activePaperId: null,
  uploading: false,
  processing: false,
  summaryResult: null,
  translationResult: null,
  qaResult: null,
};

const paperSlice = createSlice({
  name: 'paper',
  initialState,
  reducers: {
    setPapers: (state, action: PayloadAction<Paper[]>) => {
      state.papers = action.payload;
    },
    addPaper: (state, action: PayloadAction<Paper>) => {
      state.papers.unshift(action.payload);
    },
    setActivePaper: (state, action: PayloadAction<string | null>) => {
      state.activePaperId = action.payload;
    },
    setUploading: (state, action: PayloadAction<boolean>) => {
      state.uploading = action.payload;
    },
    setProcessing: (state, action: PayloadAction<boolean>) => {
      state.processing = action.payload;
    },
    setSummaryResult: (state, action: PayloadAction<ToolResult | null>) => {
      state.summaryResult = action.payload;
    },
    setTranslationResult: (state, action: PayloadAction<ToolResult | null>) => {
      state.translationResult = action.payload;
    },
    setQaResult: (state, action: PayloadAction<ToolResult | null>) => {
      state.qaResult = action.payload;
    },
  },
});

export const { setPapers, addPaper, setActivePaper, setUploading, setProcessing, setSummaryResult, setTranslationResult, setQaResult } = paperSlice.actions;
export default paperSlice.reducer;
