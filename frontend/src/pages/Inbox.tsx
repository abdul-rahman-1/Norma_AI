import { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageSquare, User, Clock, AlertCircle, CheckCircle2, 
  Search, Filter, ChevronRight, Phone, Calendar, 
  ShieldCheck, BrainCircuit, ArrowUpRight, Send, Loader2, X, Sparkles, Lock
} from 'lucide-react';
import { cn } from '../utils/cn';
import { useAuth } from '../contexts/AuthContext';

export default function Inbox() {
  const [threads, setThreads] = useState<any[]>([]);
  const [activeThread, setActiveThread] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [msgLoading, setMsgLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { token } = useAuth();

  const fetchThreads = useCallback(async () => {
    if (!token) return;
    try {
      const res = await axios.get('/api/messages/threads', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setThreads(res.data);
      if (res.data.length > 0 && !activeThread) {
        setActiveThread(res.data[0]);
      }
    } catch (err) {
      console.error('Failed to sync threads', err);
    } finally {
      setLoading(false);
    }
  }, [token, activeThread]);

  const fetchMessages = useCallback(async (phone: string) => {
    if (!token) return;
    setMsgLoading(true);
    try {
      const res = await axios.get(`/api/messages/${phone}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessages(res.data);
    } catch (err) {
      console.error('Failed to fetch history', err);
    } finally {
      setMsgLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchThreads();
    const interval = setInterval(fetchThreads, 15000); // Polling for updates
    return () => clearInterval(interval);
  }, [fetchThreads]);

  useEffect(() => {
    if (activeThread) {
      fetchMessages(activeThread._id);
    }
  }, [activeThread, fetchMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="p-12 rounded-[3rem] animate-pulse">
          <Loader2 className="animate-spin text-blue-600" size={40} />
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="h-[calc(100vh-140px)] flex flex-col lg:flex-row gap-8"
    >
      {/* Left Pane: Threads List */}
      <div className="w-full lg:w-1/3 h-full rounded-[3rem] border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden bg-white dark:bg-gray-800 shadow-xl">
        <div className="p-8 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-black text-slate-800 dark:text-white uppercase tracking-tighter italic flex items-center gap-3">
              <MessageSquare size={24} className="text-blue-600" />
              Communications
            </h2>
          </div>
          
          <div className="flex items-center gap-3 bg-white dark:bg-gray-900 px-5 py-3 rounded-[1.5rem] border border-gray-200 dark:border-gray-700 focus-within:border-blue-200 focus-within:ring-4 focus-within:ring-blue-500/5 transition-all">
            <Search size={16} className="text-slate-400" />
            <input type="text" placeholder="Search patients..." className="bg-transparent border-none outline-none text-sm w-full text-slate-700 dark:text-gray-200 font-medium placeholder-slate-400" />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
          {threads.length > 0 ? threads.map(thread => (
            <motion.div 
              key={thread._id}
              whileHover={{ scale: 1.02 }}
              onClick={() => setActiveThread(thread)}
              className={cn(
                "p-5 rounded-[2rem] cursor-pointer transition-all duration-300 border border-transparent group",
                activeThread?._id === thread._id 
                  ? "bg-blue-50 dark:bg-blue-900/20 shadow-xl shadow-blue-500/5 border-blue-100 dark:border-blue-900/50" 
                  : "hover:bg-gray-50 dark:hover:bg-gray-700/50"
              )}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <div className="w-10 h-10 rounded-xl bg-zinc-900 dark:bg-blue-600 flex items-center justify-center text-[10px] font-black text-white shadow-lg group-hover:scale-110 transition-transform">
                      {thread.sender_name?.split(' ').map((n: any) => n[0]).join('') || 'U'}
                    </div>
                    {thread.unread_count > 0 && <span className="absolute -top-1 -right-1 w-3.5 h-3.5 bg-blue-500 rounded-full border-2 border-white dark:border-gray-800 animate-pulse" />}
                  </div>
                  <div>
                    <h3 className="text-sm font-black text-slate-800 dark:text-white leading-none">{thread.sender_name || 'Unknown'}</h3>
                    <p className="text-[9px] font-bold text-slate-400 dark:text-gray-500 uppercase tracking-widest mt-1.5">{thread._id}</p>
                  </div>
                </div>
                <span className="text-[9px] font-black text-slate-300 dark:text-gray-600 uppercase">{new Date(thread.last_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
              <p className="text-xs text-slate-500 dark:text-gray-400 font-medium line-clamp-1 mt-3 pl-13 opacity-70 italic">"{thread.last_message}"</p>
            </motion.div>
          )) : (
            <div className="h-full flex flex-col items-center justify-center opacity-20 grayscale scale-75">
               <Sparkles size={64} className="text-slate-300 mb-4" />
               <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 text-center">No communications identified</p>
            </div>
          )}
        </div>
      </div>

      {/* Right Pane: Conversation History (Read Only) */}
      <div className="flex-1 h-full rounded-[3rem] border border-gray-200 dark:border-gray-700 flex flex-col overflow-hidden bg-white dark:bg-gray-800 shadow-xl relative">
        
        {activeThread ? (
          <>
            {/* Chat Header */}
            <div className="p-8 border-b border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 flex justify-between items-center z-10 relative">
              <div className="flex items-center gap-5">
                <div className="w-14 h-14 rounded-[1.5rem] bg-gray-50 dark:bg-gray-900 border border-gray-100 dark:border-gray-700 flex items-center justify-center text-lg font-black text-blue-600 dark:text-blue-400 shadow-inner">
                  {activeThread.sender_name?.split(' ').map((n: any) => n[0]).join('') || 'U'}
                </div>
                <div>
                  <h2 className="text-2xl font-black text-slate-800 dark:text-white tracking-tight">{activeThread.sender_name || 'Patient'}</h2>
                  <p className="text-[10px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest mt-1.5 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
                    Read-Only Access
                  </p>
                </div>
              </div>
            </div>

            {/* Chat History */}
            <div className="flex-1 overflow-y-auto p-10 space-y-8 z-10 scrollbar-thin relative bg-gray-50/30 dark:bg-gray-900/20">
              <div className="flex justify-center mb-12">
                <span className="text-[9px] font-black text-slate-300 dark:text-gray-600 uppercase tracking-[0.3em] bg-white dark:bg-gray-800 px-6 py-2.5 rounded-full border border-gray-100 dark:border-gray-700 shadow-sm">
                   Archive History Log
                </span>
              </div>

              <AnimatePresence initial={false}>
                {messages.map((msg, i) => (
                  <motion.div 
                    key={msg._id || i}
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    className={cn(
                      "flex items-end gap-4",
                      msg.direction === 'outbound' ? "justify-end" : "justify-start"
                    )}
                  >
                    {msg.direction === 'inbound' && (
                       <div className="w-10 h-10 rounded-xl bg-zinc-900 dark:bg-blue-600 flex items-center justify-center text-[10px] font-black text-blue-400 dark:text-blue-200 shadow-xl flex-shrink-0">
                          {(activeThread.sender_name || 'P')[0]}
                       </div>
                    )}
                    <div className={cn(
                      "max-w-[70%] p-6 rounded-[2.2rem] shadow-xl transition-all hover:scale-[1.02]",
                      msg.direction === 'outbound' 
                        ? "bg-zinc-900 dark:bg-blue-600 text-white rounded-br-md shadow-zinc-900/10" 
                        : "bg-white dark:bg-gray-800 text-slate-700 dark:text-gray-200 rounded-bl-md border border-gray-100 dark:border-gray-700 shadow-blue-500/5"
                    )}>
                      <div className="flex justify-between items-start mb-2 gap-4">
                        <p className="text-sm font-medium leading-relaxed">{msg.content}</p>
                        {msg.sentiment && msg.sentiment !== 'neutral' && (
                          <span className={cn(
                            "px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-tighter shrink-0",
                            msg.sentiment === 'urgent' ? "bg-red-500 text-white animate-pulse" :
                            msg.sentiment === 'positive' ? "bg-green-100 text-green-700" :
                            msg.sentiment === 'negative' ? "bg-orange-100 text-orange-700" : "bg-gray-100 text-gray-600"
                          )}>
                            {msg.sentiment}
                          </span>
                        )}
                      </div>
                      <span className={cn(
                        "text-[9px] font-black uppercase mt-3 block tracking-widest opacity-40",
                        msg.direction === 'outbound' ? "text-right" : "text-left"
                      )}>
                        {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>

            {/* Read-Only Footer */}
            <div className="p-8 bg-zinc-50 dark:bg-gray-900 border-t border-gray-100 dark:border-gray-700 z-10 flex items-center justify-center gap-4">
              <Lock size={16} className="text-zinc-400" />
              <p className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Direct replies are disabled. Use the dashboard to manage patient records.</p>
            </div>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center space-y-6 bg-gray-50 dark:bg-gray-900/20">
             <div className="p-10 rounded-[3rem] text-slate-200 dark:text-gray-800 border border-gray-100 dark:border-gray-800 shadow-inner bg-white dark:bg-gray-800">
                <MessageSquare size={64} />
             </div>
             <p className="text-[10px] font-black text-slate-400 dark:text-gray-600 uppercase tracking-[0.5em]">Select a record to view history</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
