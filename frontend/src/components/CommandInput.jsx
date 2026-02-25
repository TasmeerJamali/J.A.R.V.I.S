import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Terminal } from 'lucide-react';

const CommandInput = ({ onSendCommand, disabled }) => {
    const [text, setText] = useState('');
    const inputRef = useRef(null);

    useEffect(() => {
        const handleKeyDown = (e) => {
            // Focus input on '/' key
            if (e.key === '/' && document.activeElement !== inputRef.current) {
                e.preventDefault();
                inputRef.current?.focus();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        const trimmed = text.trim();
        if (trimmed && !disabled) {
            onSendCommand(trimmed);
            setText('');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="relative">
            <div className="flex items-center bg-black/60 backdrop-blur-sm border border-cyan-500/20 rounded-lg overflow-hidden focus-within:border-cyan-500/50 transition-colors">
                <Terminal size={14} className="text-cyan-500/50 ml-3 flex-shrink-0" />
                <input
                    ref={inputRef}
                    type="text"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder='Type a command... (press "/" to focus)'
                    disabled={disabled}
                    className="flex-1 bg-transparent text-cyan-100 text-xs font-mono px-3 py-3 outline-none placeholder-gray-600 disabled:opacity-50"
                />
                <motion.button
                    type="submit"
                    disabled={!text.trim() || disabled}
                    className="px-3 py-3 text-cyan-400 disabled:text-gray-700 transition-colors hover:text-cyan-300"
                    whileTap={{ scale: 0.9 }}
                >
                    <Send size={14} />
                </motion.button>
            </div>
        </form>
    );
};

export default CommandInput;
