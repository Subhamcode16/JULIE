import React, { useEffect, useState } from 'react';
import { getCurrentWindow } from '@tauri-apps/api/window';

// Setup WebSocket to listen for cursor position
const WS_PORT = 8000; // Fastapi backend port

export default function CursorOverlay() {
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isActive, setIsActive] = useState(false);
  const [isAIControlled, setIsAIControlled] = useState(false);

  useEffect(() => {
    // Only connect if we are the ai-cursor window
    const appWindow = getCurrentWindow();
    if (appWindow.label !== 'ai-cursor') return;

    let ws: WebSocket;
    let reconnectTimeout: ReturnType<typeof setTimeout>;

    const connect = () => {
      ws = new WebSocket(`ws://localhost:${WS_PORT}/ws/cursor`);

      ws.onopen = () => {
        console.log("Cursor WebSocket Connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'cursor_update') {
            setPosition({ x: data.x, y: data.y });
            setIsActive(data.is_active !== undefined ? data.is_active : true);
            setIsAIControlled(data.is_ai_controlled || false);
          }
        } catch (e) {
          console.error("Cursor WS Parse error", e);
        }
      };

      ws.onclose = () => {
        console.log("Cursor WebSocket Disconnected, reconnecting in 1s...");
        reconnectTimeout = setTimeout(connect, 1000);
      };
    };

    connect();

    return () => {
      if (ws) ws.close();
      clearTimeout(reconnectTimeout);
    };
  }, []);

  if (!isActive) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        pointerEvents: 'none',
        overflow: 'hidden',
        zIndex: 9999,
      }}
    >
      {/* AI Cursor Representation */}
      <div
        style={{
          position: 'absolute',
          left: position.x,
          top: position.y,
          width: '24px',
          height: '24px',
          borderRadius: '50%',
          border: isAIControlled ? '3px solid #ff00ff' : '2px solid rgba(0, 255, 255, 0.6)',
          backgroundColor: isAIControlled ? 'rgba(255, 0, 255, 0.2)' : 'transparent',
          transform: 'translate(-50%, -50%)',
          boxShadow: isAIControlled 
            ? '0 0 15px #ff00ff, inset 0 0 10px #ff00ff' 
            : '0 0 8px rgba(0, 255, 255, 0.4)',
          transition: isAIControlled ? 'all 0.1s linear' : 'all 0.05s linear',
        }}
      >
        {isAIControlled && (
          <div style={{
            position: 'absolute',
            top: '110%',
            left: '50%',
            transform: 'translateX(-50%)',
            color: '#ff00ff',
            fontSize: '10px',
            fontWeight: 'bold',
            textShadow: '0 0 3px black',
            whiteSpace: 'nowrap'
          }}>
            SIXTEEN
          </div>
        )}
      </div>
    </div>
  );
}
