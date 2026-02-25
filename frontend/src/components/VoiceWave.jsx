import React from 'react';
import { motion } from 'framer-motion';

const VoiceWave = ({ state }) => {
    const isActive = state === 'listening' || state === 'speaking' || state === 'wake_detected';

    const barVariants = {
        idle: { scaleY: 0.2, transition: { duration: 0.3 } },
        active: (i) => ({
            scaleY: [0.3, 1, 0.3],
            transition: {
                duration: 0.6 + Math.random() * 0.4,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: i * 0.08,
            },
        }),
    };

    const getColor = () => {
        switch (state) {
            case 'listening': return '#22d3ee';
            case 'speaking': return '#22c55e';
            case 'wake_detected': return '#ef4444';
            case 'recognized': return '#eab308';
            default: return '#374151';
        }
    };

    const getLabel = () => {
        switch (state) {
            case 'listening': return 'LISTENING';
            case 'speaking': return 'SPEAKING';
            case 'wake_detected': return 'WAKE WORD';
            case 'recognized': return 'RECOGNIZED';
            default: return 'STANDBY';
        }
    };

    return (
        <div className="flex flex-col items-center gap-2">
            <div className="flex items-end justify-center gap-[3px] h-8">
                {Array.from({ length: 16 }).map((_, i) => (
                    <motion.div
                        key={i}
                        className="w-[3px] rounded-full origin-bottom"
                        style={{ backgroundColor: getColor() }}
                        custom={i}
                        variants={barVariants}
                        animate={isActive ? 'active' : 'idle'}
                    />
                ))}
            </div>
            <motion.span
                className="text-[10px] font-mono tracking-[0.3em] uppercase"
                style={{ color: getColor() }}
                animate={{ opacity: isActive ? [0.5, 1, 0.5] : 0.5 }}
                transition={{ duration: 1.5, repeat: Infinity }}
            >
                {getLabel()}
            </motion.span>
        </div>
    );
};

export default VoiceWave;
