import React, { useState, useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';
import { motion, AnimatePresence } from 'framer-motion';
import { Monitor, MonitorOff } from 'lucide-react';
import ArcReactor from './components/ArcReactor';
import TargetLock from './components/TargetLock';
import StatusPanel from './components/StatusPanel';
import CommandLog from './components/CommandLog';
import VoiceWave from './components/VoiceWave';
import BrainActivity from './components/BrainActivity';
import CommandInput from './components/CommandInput';
import './App.css';

const BACKEND_URL = 'http://localhost:8000';
const socket = io(BACKEND_URL, {
    reconnection: true,
    reconnectionDelay: 2000,
    reconnectionAttempts: 10,
});

function App() {
    const [connected, setConnected] = useState(false);
    const [isHUD, setIsHUD] = useState(true);
    const [target, setTarget] = useState(null);
    const [voiceState, setVoiceState] = useState('idle');
    const [commands, setCommands] = useState([]);
    const [brainActivity, setBrainActivity] = useState({ status: 'standby' });
    const [systemState, setSystemState] = useState({
        wake_word: { value: 'LISTENING', color: 'green' },
        voice: { value: 'IDLE', color: 'yellow' },
        brain: { value: 'STANDBY', color: 'yellow' },
        security: { value: 'MONITORING', color: 'cyan' },
        perception: { value: 'ACTIVE', color: 'magenta' },
        connection: { value: 'OFFLINE', color: 'red' },
    });
    const [notifications, setNotifications] = useState([]);

    // Socket.IO event handlers
    useEffect(() => {
        socket.on('connect', () => {
            console.log('[Socket] Connected to backend');
            setConnected(true);
            setSystemState(prev => ({
                ...prev,
                connection: { value: 'ONLINE', color: 'green' },
            }));
        });

        socket.on('disconnect', () => {
            console.log('[Socket] Disconnected from backend');
            setConnected(false);
            setSystemState(prev => ({
                ...prev,
                connection: { value: 'OFFLINE', color: 'red' },
            }));
        });

        socket.on('status', (data) => {
            if (data.state) {
                const mapped = {};
                Object.entries(data.state).forEach(([key, value]) => {
                    mapped[key] = { value, color: 'cyan' };
                });
                setSystemState(prev => ({ ...prev, ...mapped }));
            }
        });

        socket.on('status_update', (data) => {
            setSystemState(prev => ({
                ...prev,
                [data.key]: { value: data.value, color: data.color },
            }));
        });

        socket.on('voice_activity', (data) => {
            setVoiceState(data.state);
        });

        socket.on('command_log', (entry) => {
            setCommands(prev => [...prev.slice(-99), entry]);
        });

        socket.on('command_received', (entry) => {
            setCommands(prev => [...prev.slice(-99), entry]);
        });

        socket.on('brain_activity', (data) => {
            setBrainActivity(data);
        });

        socket.on('target_lock', (data) => {
            setTarget(data);
            setTimeout(() => setTarget(null), 3000);
        });

        socket.on('notification', (data) => {
            const id = Date.now();
            setNotifications(prev => [...prev, { ...data, id }]);
            setTimeout(() => {
                setNotifications(prev => prev.filter(n => n.id !== id));
            }, 5000);
        });

        return () => {
            socket.off('connect');
            socket.off('disconnect');
            socket.off('status');
            socket.off('status_update');
            socket.off('voice_activity');
            socket.off('command_log');
            socket.off('command_received');
            socket.off('brain_activity');
            socket.off('target_lock');
            socket.off('notification');
        };
    }, []);

    const handleSendCommand = useCallback((text) => {
        socket.emit('send_command', { text });
        setCommands(prev => [...prev.slice(-99), {
            text,
            source: 'frontend',
            timestamp: Date.now() / 1000,
            type: 'user',
        }]);
    }, []);

    return (
        <div className="app-container">
            {/* Target Lock Overlay */}
            <AnimatePresence>
                {target && (
                    <TargetLock
                        x={target.x}
                        y={target.y}
                        width={target.width}
                        height={target.height}
                        label={target.label}
                    />
                )}
            </AnimatePresence>

            {/* Notifications */}
            <div className="fixed top-4 right-4 z-50 space-y-2">
                <AnimatePresence>
                    {notifications.map((notif) => (
                        <motion.div
                            key={notif.id}
                            initial={{ opacity: 0, x: 50 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 50 }}
                            className={`px-4 py-2 rounded-lg border font-mono text-xs backdrop-blur-sm ${
                                notif.level === 'warning'
                                    ? 'border-yellow-500/30 bg-yellow-900/20 text-yellow-400'
                                    : notif.level === 'error'
                                    ? 'border-red-500/30 bg-red-900/20 text-red-400'
                                    : notif.level === 'proactive'
                                    ? 'border-purple-500/30 bg-purple-900/20 text-purple-400'
                                    : 'border-cyan-500/30 bg-cyan-900/20 text-cyan-400'
                            }`}
                        >
                            {notif.message}
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>

            {/* HUD Toggle */}
            <button
                onClick={() => setIsHUD(prev => !prev)}
                className="fixed top-4 left-4 z-50 p-2 rounded-lg border border-cyan-500/20 bg-black/40 backdrop-blur-sm text-cyan-400 hover:border-cyan-500/50 transition-colors"
                title={isHUD ? 'Switch to Reactor View' : 'Switch to HUD View'}
            >
                {isHUD ? <MonitorOff size={16} /> : <Monitor size={16} />}
            </button>

            {/* Connection indicator */}
            <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`} />
                <span className={`text-[10px] font-mono tracking-[0.3em] uppercase ${connected ? 'text-green-400' : 'text-red-500'}`}>
                    {connected ? 'CONNECTED' : 'DISCONNECTED'}
                </span>
            </div>

            <AnimatePresence mode="wait">
                {isHUD ? (
                    <motion.div
                        key="hud"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="hud-layout"
                    >
                        {/* Top bar */}
                        <div className="hud-topbar">
                            <div className="flex items-center gap-3">
                                <span className="text-cyan-400 font-mono text-sm font-bold tracking-[0.3em]">
                                    J.A.R.V.I.S.
                                </span>
                                <span className="text-gray-600 font-mono text-[10px] tracking-wider">
                                    v3.0 CLOUD INTELLIGENCE
                                </span>
                            </div>
                            <VoiceWave state={voiceState} />
                            <div className="text-gray-500 font-mono text-[10px]">
                                {new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                            </div>
                        </div>

                        {/* Main content area */}
                        <div className="hud-main">
                            {/* Left panel */}
                            <div className="hud-sidebar-left">
                                <StatusPanel systemState={systemState} />
                                <BrainActivity activity={brainActivity} />
                            </div>

                            {/* Center - Arc Reactor (smaller) */}
                            <div className="hud-center">
                                <div className="scale-[0.6] transform">
                                    <ArcReactor />
                                </div>
                            </div>

                            {/* Right panel */}
                            <div className="hud-sidebar-right">
                                <CommandLog commands={commands} />
                            </div>
                        </div>

                        {/* Bottom bar - Command input */}
                        <div className="hud-bottombar">
                            <CommandInput
                                onSendCommand={handleSendCommand}
                                disabled={!connected}
                            />
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="reactor"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="reactor-view"
                    >
                        <ArcReactor />
                        <div className="fixed bottom-24 left-1/2 -translate-x-1/2">
                            <VoiceWave state={voiceState} />
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default App;
