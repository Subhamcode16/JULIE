import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import CursorOverlay from './components/CursorOverlay'
import './index.css'
import { getCurrentWindow } from '@tauri-apps/api/window'

function Root() {
  const [windowLabel, setWindowLabel] = useState<string | null>(null);

  useEffect(() => {
    // Tauri v2 API
    const label = getCurrentWindow().label;
    setWindowLabel(label);
  }, []);

  if (!windowLabel) return null;

  if (windowLabel === 'ai-cursor') {
    return <CursorOverlay />;
  }

  return <App />;
}

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
)
