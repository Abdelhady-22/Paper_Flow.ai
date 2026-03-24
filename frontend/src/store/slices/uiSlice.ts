import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UiState {
  sidebarOpen: boolean;
  activeTab: 'chat' | 'tools' | 'discover';
  language: 'en' | 'ar';
  theme: 'dark';
}

const initialState: UiState = {
  sidebarOpen: true,
  activeTab: 'chat',
  language: 'en',
  theme: 'dark',
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setActiveTab: (state, action: PayloadAction<'chat' | 'tools' | 'discover'>) => {
      state.activeTab = action.payload;
    },
    setLanguage: (state, action: PayloadAction<'en' | 'ar'>) => {
      state.language = action.payload;
    },
  },
});

export const { toggleSidebar, setActiveTab, setLanguage } = uiSlice.actions;
export default uiSlice.reducer;
