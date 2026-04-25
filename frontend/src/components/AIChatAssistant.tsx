import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

export default function AIChatAssistant() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'NORMA AI Sentinel active. High-fidelity clinical orchestration engaged. How can I assist?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const res = await axios.post('http://localhost:5000/api/webhook/whatsapp', {
        From: 'web-terminal',
        Body: userMessage
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply || "Clinical protocol executed. Mesh data updated." }]);
    } catch (err) {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', content: "Neural link interrupted. Please check clinical mesh connection." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Button */}
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-8 right-8 w-16 h-16 rounded-xl flex items-center justify-center transition-all duration-500 shadow-2xl z-50 border ${
          isOpen ? 'bg-black border-zinc-800' : 'bg-black hover:bg-[#7c3aed] border-transparent hover:-translate-y-1'
        }`}
      >
        {isOpen ? <X className="text-white" /> : <MessageSquare className="text-white" />}
        {!isOpen && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-[#7c3aed] rounded-full border-2 border-white animate-pulse" />
        )}
      </button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            className="fixed bottom-28 right-8 w-[420px] h-[600px] bg-white rounded-[2.5rem] shadow-[0_40px_100px_rgba(0,0,0,0.2)] flex flex-col overflow-hidden z-50 border border-zinc-100"
          >
            {/* Header */}
            <div className="p-8 border-b border-zinc-100 bg-white flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-black flex items-center justify-center text-white shadow-lg">
                  <Bot size={24} />
                </div>
                <div>
                  <p className="text-sm font-black text-black leading-tight uppercase tracking-widest italic">Sentinel AI</p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-[#7c3aed] animate-pulse shadow-[0_0_8px_rgba(124,58,237,0.5)]" />
                    <p className="text-[9px] text-zinc-400 font-black uppercase tracking-[0.2em]">Clinical Link Active</p>
                  </div>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="bg-zinc-50 p-2 rounded-xl text-zinc-400 hover:text-black border border-zinc-100 transition-all">
                <X size={20} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-white scrollbar-thin">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] p-5 rounded-2xl text-sm leading-relaxed border ${
                    msg.role === 'user' 
                      ? 'bg-black border-black text-white font-medium rounded-br-none shadow-xl' 
                      : 'bg-zinc-50 border-zinc-100 text-black rounded-bl-none shadow-sm'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-zinc-50 text-zinc-400 p-5 rounded-2xl rounded-bl-none border border-zinc-100 flex items-center gap-3">
                    <Loader2 size={16} className="animate-spin text-[#7c3aed]" />
                    <span className="text-[9px] font-black uppercase tracking-[0.3em]">Processing Neural Patterns...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="p-6 bg-zinc-50 border-t border-zinc-100">
              <div className="relative flex items-center gap-4">
                <div className="flex-1 relative group">
                  <Sparkles size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-300 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Authorize inquiry..."
                    className="w-full bg-white border border-zinc-200 text-black pl-12 pr-6 py-4 rounded-xl outline-none focus:border-black transition-all text-xs font-bold uppercase tracking-widest placeholder-zinc-300"
                  />
                </div>
                <button 
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="w-14 h-14 bg-black text-white rounded-xl flex items-center justify-center hover:bg-[#7c3aed] transition-all disabled:opacity-30 shadow-xl active:scale-95"
                >
                  <Send size={20} />
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
