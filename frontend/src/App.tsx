import { Provider } from 'react-redux';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import { store } from './store';
import { ThemeProvider } from './context/ThemeContext';
import WelcomePage from './pages/WelcomePage';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import ResearchPage from './pages/ResearchPage';
import SummarizePage from './pages/SummarizePage';
import TranslatePage from './pages/TranslatePage';
import OcrPage from './pages/OcrPage';
import QaGeneratorPage from './pages/QaGeneratorPage';
import DiscoverPage from './pages/DiscoverPage';
import Footer from './components/Footer';
import './index.css';

function AnimatedRoutes() {
  const location = useLocation();
  const hideFooter = ['/chat', '/research'].some(r => location.pathname.startsWith(r));

  return (
    <>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<WelcomePage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/research" element={<ResearchPage />} />
          <Route path="/summarize" element={<SummarizePage />} />
          <Route path="/translate" element={<TranslatePage />} />
          <Route path="/ocr" element={<OcrPage />} />
          <Route path="/qa-generator" element={<QaGeneratorPage />} />
          <Route path="/discover" element={<DiscoverPage />} />
        </Routes>
      </AnimatePresence>
      {!hideFooter && <Footer />}
    </>
  );
}

function App() {
  return (
    <Provider store={store}>
      <ThemeProvider>
        <BrowserRouter>
          <AnimatedRoutes />
          <Toaster position="top-right" toastOptions={{
            style: {
              background: 'var(--current-card-bg)',
              color: 'var(--current-text-primary)',
              border: '1px solid var(--current-border)',
              borderRadius: '12px',
            },
          }} />
        </BrowserRouter>
      </ThemeProvider>
    </Provider>
  );
}

export default App;
