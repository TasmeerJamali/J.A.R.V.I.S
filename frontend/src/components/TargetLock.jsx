import React from 'react';
import { motion } from 'framer-motion';

const TargetLock = ({ x, y, width, height, label }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 1.5 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.5 }}
            style={{
                position: 'absolute',
                left: x,
                top: y,
                width: width,
                height: height,
                pointerEvents: 'none', // Let clicks pass through
                zIndex: 9999,
            }}
        >
            {/* Corners */}
            <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-red-500" />
            <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-red-500" />
            <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-red-500" />
            <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-red-500" />

            {/* Center Crosshair */}
            <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-2 h-2 bg-red-500 rounded-full opacity-50" />
            </div>

            {/* Label */}
            <div className="absolute -top-6 left-0 text-red-500 text-xs font-mono bg-black/50 px-1">
                TARGET: {label}
            </div>

            {/* Scanline Animation */}
            <motion.div
                className="absolute inset-0 bg-red-500/10"
                animate={{ top: ['0%', '100%'] }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                style={{ height: '2px' }}
            />
        </motion.div>
    );
};

export default TargetLock;
