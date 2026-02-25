import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Mic, Brain, Shield, Eye, Wifi } from 'lucide-react';

const statusIcons = {
    wake_word: Mic,
    voice: Activity,
    brain: Brain,
    security: Shield,
    perception: Eye,
    connection: Wifi,
};

const statusColors = {
    green: '#22c55e',
    cyan: '#22d3ee',
    yellow: '#eab308',
    red: '#ef4444',
    magenta: '#d946ef',
};

const StatusItem = ({ label, value, color }) => {
    const Icon = statusIcons[label] || Activity;
    const dotColor = statusColors[color] || statusColors.cyan;

    return (
        <motion.div
            className="flex items-center gap-3 py-1.5 px-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            layout
        >
            <Icon size={14} style={{ color: dotColor }} />
            <span className="text-gray-500 text-xs font-mono uppercase tracking-wider w-24">
                {label.replace('_', ' ')}
            </span>
            <motion.span
                className="text-xs font-mono font-bold tracking-wider"
                style={{ color: dotColor }}
                key={value}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                {value}
            </motion.span>
            <motion.div
                className="w-1.5 h-1.5 rounded-full ml-auto"
                style={{ backgroundColor: dotColor }}
                animate={{ opacity: [1, 0.3, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
            />
        </motion.div>
    );
};

const StatusPanel = ({ systemState }) => {
    const defaultState = {
        wake_word: { value: 'LISTENING', color: 'green' },
        voice: { value: 'IDLE', color: 'yellow' },
        brain: { value: 'STANDBY', color: 'yellow' },
        security: { value: 'MONITORING', color: 'cyan' },
        perception: { value: 'ACTIVE', color: 'magenta' },
        connection: { value: 'ONLINE', color: 'green' },
    };

    const state = { ...defaultState, ...systemState };

    return (
        <div className="bg-black/60 backdrop-blur-sm border border-cyan-500/20 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2 px-3">
                <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                <span className="text-cyan-400 text-xs font-mono tracking-[0.2em] uppercase">
                    System Status
                </span>
            </div>
            <div className="space-y-0.5">
                {Object.entries(state).map(([key, { value, color }]) => (
                    <StatusItem key={key} label={key} value={value} color={color} />
                ))}
            </div>
        </div>
    );
};

export default StatusPanel;
