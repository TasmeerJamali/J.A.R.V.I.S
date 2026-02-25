import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Bot, Zap, AlertTriangle } from 'lucide-react';

const typeConfig = {
    user: { icon: User, color: '#22d3ee', label: 'YOU' },
    response: { icon: Bot, color: '#22c55e', label: 'JARVIS' },
    action: { icon: Zap, color: '#eab308', label: 'ACTION' },
    error: { icon: AlertTriangle, color: '#ef4444', label: 'ERROR' },
};

const CommandEntry = ({ entry }) => {
    const config = typeConfig[entry.type] || typeConfig.response;
    const Icon = config.icon;
    const timeStr = new Date(entry.timestamp * 1000).toLocaleTimeString('en-US', {
        hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
    });

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex gap-2 py-1.5 px-2 hover:bg-white/5 rounded"
        >
            <Icon size={12} style={{ color: config.color, marginTop: 3, flexShrink: 0 }} />
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono font-bold tracking-wider" style={{ color: config.color }}>
                        {config.label}
                    </span>
                    <span className="text-[10px] text-gray-600 font-mono">{timeStr}</span>
                </div>
                <p className="text-xs text-gray-300 font-mono leading-relaxed break-words">
                    {entry.text}
                </p>
            </div>
        </motion.div>
    );
};

const CommandLog = ({ commands }) => {
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [commands]);

    return (
        <div className="bg-black/60 backdrop-blur-sm border border-cyan-500/20 rounded-lg flex flex-col h-full">
            <div className="flex items-center gap-2 p-3 border-b border-cyan-500/10">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-cyan-400 text-xs font-mono tracking-[0.2em] uppercase">
                    Command Log
                </span>
                <span className="text-gray-600 text-[10px] font-mono ml-auto">
                    {commands.length} entries
                </span>
            </div>
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin scrollbar-thumb-cyan-500/20"
                style={{ maxHeight: '300px' }}
            >
                <AnimatePresence initial={false}>
                    {commands.length === 0 ? (
                        <div className="flex items-center justify-center h-full py-8">
                            <p className="text-gray-600 text-xs font-mono">
                                Awaiting commands...
                            </p>
                        </div>
                    ) : (
                        commands.map((cmd, i) => (
                            <CommandEntry key={cmd.id || `${cmd.timestamp}-${i}`} entry={cmd} />
                        ))
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default CommandLog;
