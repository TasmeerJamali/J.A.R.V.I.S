import React from 'react';
import { motion } from 'framer-motion';

const ArcReactor = () => {
    return (
        <div className="flex items-center justify-center h-screen w-screen bg-transparent overflow-hidden">
            {/* Container for the reactor */}
            <div className="relative w-64 h-64 flex items-center justify-center">

                {/* Outer Ring - Rotating */}
                <motion.div
                    className="absolute w-full h-full rounded-full border-4 border-cyan-500/30 border-t-cyan-400 border-b-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.5)]"
                    animate={{ rotate: 360 }}
                    transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
                />

                {/* Inner Ring - Rotating Counter-Clockwise */}
                <motion.div
                    className="absolute w-48 h-48 rounded-full border-2 border-blue-500/40 border-l-blue-400 border-r-blue-400 shadow-[0_0_15px_rgba(59,130,246,0.5)]"
                    animate={{ rotate: -360 }}
                    transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                />

                {/* Core Glow */}
                <motion.div
                    className="absolute w-32 h-32 rounded-full bg-cyan-400/10 blur-xl"
                    animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                />

                {/* Core Structure */}
                <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-cyan-900 to-black border border-cyan-500/50 flex items-center justify-center shadow-[0_0_30px_rgba(34,211,238,0.8)]">
                    <div className="w-16 h-16 rounded-full bg-cyan-400/20 shadow-inner border border-cyan-300/30 backdrop-blur-sm"></div>

                    {/* Triangular details (simplified) */}
                    <div className="absolute inset-0 flex items-center justify-center">
                        <svg viewBox="0 0 100 100" className="w-full h-full p-2 opacity-80">
                            <circle cx="50" cy="50" r="40" stroke="cyan" strokeWidth="1" fill="none" />
                            <path d="M50 10 L90 80 L10 80 Z" stroke="cyan" strokeWidth="1" fill="none" className="drop-shadow-[0_0_5px_cyan]" />
                        </svg>
                    </div>
                </div>

            </div>

            {/* Status Text */}
            <motion.div
                className="absolute bottom-10 text-cyan-400 font-mono text-sm tracking-[0.3em] uppercase drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]"
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
            >
                J.A.R.V.I.S. Online
            </motion.div>
        </div>
    );
};

export default ArcReactor;
