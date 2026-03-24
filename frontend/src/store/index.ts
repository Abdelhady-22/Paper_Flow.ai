import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './slices/chatSlice';
import paperReducer from './slices/paperSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    chat: chatReducer,
    paper: paperReducer,
    ui: uiReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
