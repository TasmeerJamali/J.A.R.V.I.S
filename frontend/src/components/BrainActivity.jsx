import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Loader, CheckCircle, AlertCircle, Sparkles } from 'lucide-react';

const statusConfig = {
    thinking: { icon: Loader, color: '#22d3ee', label: 'THINKING', spin: true },
    executing: { icon: Sparkles, color: '#eab308', label: 'EXECUTING', spin: false },
    standby: { icon: Brain, color: '#6b7280', label: 'STANDBY', spin: false },
    proactive: { icon: Sparkles, color: '#d946ef', label: 'PROACTIVE', spin: false },
    error: { icon: AlertCircle, color: '#ef4444', label: 'ERROR', spin: false },
    complete: { icon: CheckCircle, color: '#22c55e', label: 'COMPLETE', spin: false },
};

const BrainActivity = ({ activity }) => {
    const { thought = '', action = '', status = 'standby' } = activity;
    const config = statusConfig[status] || statusConfig.standby;
    const Icon = config.icon;

    return (
        <div className="bg-black/60 backdrop-blur-sm border border-cyan-500/20 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
                <motion.div
                    animate={config.spin ? { rotate: 360 } : {}}
                    transition={config.spin ? { duration: 1, repeat: Infinity, ease: 'linear' } : {}}
                >
                    <Icon size={14} style={{ color: config.color }} />
                </motion.div>
                <span className="text-xs font-mono tracking-[0.2em] uppercase" style={{ color: config.color }}>
                    Gemini Brain — {config.label}
                </span>
            </div>
            <AnimatePresence mode="wait">
                {thought && (
                    <motion.div
                        key={thought}
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="mt-1"
                    >
                        <p className="text-gray-400 text-[11px] font-mono leading-relaxed">
                            {thought}
                        </p>
                    </motion.div>
                )}
                {action && status === 'executing' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="mt-1 flex items-center gap-1"
                    >
                        <span className="text-yellow-400 text-[10px] font-mono">
                            &gt; {action}
                        </span>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default BrainActivity;
