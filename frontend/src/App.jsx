import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import ArcReactor from './components/ArcReactor';
import TargetLock from './components/TargetLock';
import './App.css';

const socket = io('http://localhost:8000');

function App() {
  const [isActive, setIsActive] = useState(false);
  const [target, setTarget] = useState(null); // { x, y, width, height, label }

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to Backend');
    });

    socket.on('status', (data) => {
      console.log('Status:', data);
    });

    socket.on('target_lock', (data) => {
      // data: { x, y, width, height, label }
      console.log('Target Lock:', data);
      setTarget(data);
      // Clear target after 3 seconds
      setTimeout(() => setTarget(null), 3000);
    });

    return () => {
      socket.off('connect');
      socket.off('status');
      socket.off('target_lock');
    };
  }, []);

  return (
    <div className="app-container relative">
      {/* Target Lock Overlay */}
      {target && (
        <TargetLock
          x={target.x}
          y={target.y}
          width={target.width}
          height={target.height}
          label={target.label}
        />
      )}

      {isActive ? (
        <div className="hud-container">
          {/* HUD will go here */}
          <h1 className="text-white">HUD ACTIVE</h1>
        </div>
      ) : (
        <ArcReactor />
      )}
    </div>
  );
}

export default App;
