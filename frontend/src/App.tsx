import { Provider } from 'react-redux';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { store } from './store';
import LandingPage from './pages/LandingPage';
import ChatPage from './pages/ChatPage';
import ToolsPage from './pages/ToolsPage';
import DiscoverPage from './pages/DiscoverPage';
import './index.css';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/tools" element={<ToolsPage />} />
          <Route path="/discover" element={<DiscoverPage />} />
        </Routes>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#111122',
              color: '#f0f0f8',
              border: '1px solid rgba(255,255,255,0.06)',
              borderRadius: '12px',
              boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
            },
          }}
        />
      </BrowserRouter>
    </Provider>
  );
}

export default App;
