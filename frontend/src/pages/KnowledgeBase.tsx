import { useState, useEffect } from 'react';
import axios from 'axios';
import { BookOpen, Plus, Search, Loader2, Save, Trash2, HelpCircle, Send, ShieldCheck, CheckCircle2, X, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { cn } from '../utils/cn';

export default function KnowledgeBase() {
  const [docs, setDocs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [newDoc, setNewDoc] = useState({ title: '', category: 'policy', content: '', tags: '' });
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState<any>(null);
  const [isQuerying, setIsQuerying] = useState(false);
  const { token } = useAuth();

  const fetchDocs = async () => {
    try {
      const res = await axios.get('/api/knowledge', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocs(res.data);
    } catch (err) {
      console.error('Failed to fetch knowledge base', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) fetchDocs();
  }, [token]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post('/api/knowledge', {
        ...newDoc,
        tags: newDoc.tags.split(',').map(t => t.trim()).filter(t => t !== '')
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsAdding(false);
      setNewDoc({ title: '', category: 'policy', content: '', tags: '' });
      fetchDocs();
    } catch (err) {
      console.error('Failed to add document', err);
    }
  };

  const handleQuery = async () => {
    if (!query) return;
    setIsQuerying(true);
    setQueryResult(null);
    try {
      const res = await axios.post('/api/knowledge/query', { question: query }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setQueryResult(res.data);
    } catch (err) {
      console.error('Query failed', err);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleDelete = async (doc_id: string) => {
    if (!confirm('Are you sure you want to delete this knowledge node?')) return;
    try {
      await axios.delete(`/api/knowledge/${doc_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDocs();
    } catch (err) {
      console.error('Failed to delete document', err);
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-12 animate-in fade-in duration-700 pb-20 px-4">
      <header className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6">
        <div>
          <h1 className="text-4xl font-black text-black dark:text-white tracking-tight uppercase italic">Clinic Intelligence</h1>
          <p className="text-zinc-500 dark:text-gray-400 mt-2 font-bold text-lg">Retrievable knowledge store for clinical grounding and policy alignment.</p>
        </div>
        <button 
          onClick={() => setIsAdding(true)}
          className="bg-black dark:bg-blue-600 text-white px-10 py-5 rounded-xl text-xs font-black uppercase tracking-[0.2em] shadow-2xl hover:bg-blue-700 transition-all flex items-center gap-4 active:scale-95"
        >
          <Plus size={18} /> Provision Node
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        <div className="lg:col-span-2 space-y-10">
          <div className="bg-white dark:bg-gray-800 rounded-[2.5rem] border-2 border-zinc-50 dark:border-gray-700 overflow-hidden shadow-sm">
            <div className="p-10 border-b border-zinc-50 dark:border-gray-700 bg-zinc-50/30 dark:bg-gray-900/20">
               <h2 className="text-2xl font-black text-black dark:text-white uppercase italic tracking-tighter">Knowledge Nodes</h2>
            </div>
            <div className="p-4 space-y-4">
              {loading ? (
                <div className="py-20 flex justify-center"><Loader2 className="animate-spin text-blue-600" size={32} /></div>
              ) : docs.length > 0 ? (
                docs.map((doc) => (
                  <div key={doc.doc_id} className="p-8 rounded-2xl bg-zinc-50/50 dark:bg-gray-900/30 hover:bg-white dark:hover:bg-gray-800 border border-transparent hover:border-zinc-100 dark:hover:border-gray-700 transition-all group relative">
                    <button 
                      onClick={() => handleDelete(doc.doc_id)}
                      className="absolute top-8 right-8 text-zinc-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
                    >
                      <Trash2 size={18} />
                    </button>
                    <div className="flex justify-between items-start mb-4">
                       <span className="px-4 py-2 rounded-lg bg-black dark:bg-blue-600 text-white text-[9px] font-black uppercase tracking-widest">{doc.category}</span>
                       <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mr-8">ID: {doc.doc_id.slice(0,8)}</span>
                    </div>
                    <h3 className="text-xl font-black text-black dark:text-white uppercase tracking-tight mb-4 italic">{doc.title}</h3>
                    <p className="text-sm text-zinc-500 dark:text-gray-400 line-clamp-3 leading-relaxed mb-6">"{doc.content}"</p>
                    <div className="flex flex-wrap gap-2">
                       {doc.tags?.map((tag: string) => (
                         <span key={tag} className="text-[9px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest bg-blue-50 dark:bg-blue-900/20 px-3 py-1 rounded-md">#{tag}</span>
                       ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="py-20 text-center text-zinc-400 italic font-bold">No intelligence nodes provisioned.</div>
              )}
            </div>
          </div>
        </div>

        <div className="space-y-10">
           {/* AI Inquiry Box */}
           <div className="bg-black dark:bg-blue-700 p-10 rounded-[2.5rem] text-white shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 blur-[50px] -mr-20 -mt-20 rounded-full" />
              <h2 className="text-2xl font-black tracking-tighter uppercase italic mb-8 relative z-10">Inquiry Engine</h2>
              <div className="space-y-6 relative z-10">
                 <textarea 
                   placeholder="Enter clinical inquiry..."
                   value={query}
                   onChange={(e) => setQuery(e.target.value)}
                   className="w-full bg-white/5 border border-white/10 rounded-2xl p-6 text-sm font-medium placeholder:text-zinc-500 focus:outline-none focus:border-white/30 min-h-[120px] transition-all resize-none"
                 />
                 <button 
                  onClick={handleQuery}
                  disabled={isQuerying || !query}
                  className="w-full bg-white text-black py-5 rounded-xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-4 hover:bg-blue-50 active:scale-95 transition-all disabled:opacity-50"
                 >
                   {isQuerying ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
                   Execute Inquiry
                 </button>
              </div>

              <AnimatePresence>
                {queryResult && (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-10 p-6 bg-white/10 rounded-2xl border border-white/10"
                  >
                     <div className="flex items-center gap-3 mb-4">
                        <CheckCircle2 size={16} className="text-blue-400" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Response Grounded</span>
                     </div>
                     <p className="text-xs font-bold leading-relaxed italic">"{queryResult.answer}"</p>
                  </motion.div>
                )}
              </AnimatePresence>
           </div>

           <div className="bg-white dark:bg-gray-800 p-10 rounded-[2.5rem] border-2 border-zinc-50 dark:border-gray-700 shadow-sm">
              <div className="flex gap-4 items-center mb-6">
                 <ShieldCheck className="text-blue-600" size={24} />
                 <h3 className="text-xs font-black text-black dark:text-white uppercase tracking-widest">Trust Matrix</h3>
              </div>
              <p className="text-[11px] text-zinc-500 dark:text-gray-400 font-bold leading-relaxed italic">
                 All knowledge nodes are end-to-end encrypted and retrieved using semantic similarity scoring (RAG).
              </p>
           </div>
        </div>
      </div>

      {/* Modal for adding new node */}
      <AnimatePresence>
        {isAdding && (
          <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-900 w-full max-w-2xl rounded-[3rem] shadow-2xl overflow-hidden border border-zinc-100 dark:border-gray-800"
            >
               <div className="p-10 border-b border-zinc-100 dark:border-gray-800 flex justify-between items-center bg-zinc-50 dark:bg-black/20">
                  <h2 className="text-2xl font-black text-black dark:text-white uppercase italic tracking-tighter">Provision Intelligence Node</h2>
                  <button onClick={() => setIsAdding(false)} className="text-zinc-400 hover:text-black dark:hover:text-white"><X size={24} /></button>
               </div>
               <form onSubmit={handleAdd} className="p-10 space-y-8">
                  <div className="space-y-2">
                     <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Node Title</label>
                     <input 
                       required
                       value={newDoc.title}
                       onChange={e => setNewDoc({...newDoc, title: e.target.value})}
                       className="w-full px-6 py-4 rounded-xl border border-zinc-100 dark:border-gray-800 bg-zinc-50 dark:bg-gray-800 focus:outline-none focus:border-blue-500 font-bold"
                       placeholder="e.g. Patient Triage Protocol"
                     />
                  </div>
                  <div className="grid grid-cols-2 gap-8">
                    <div className="space-y-2">
                      <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Category</label>
                      <select 
                        value={newDoc.category}
                        onChange={e => setNewDoc({...newDoc, category: e.target.value})}
                        className="w-full px-6 py-4 rounded-xl border border-zinc-100 dark:border-gray-800 bg-zinc-50 dark:bg-gray-800 focus:outline-none focus:border-blue-500 font-bold"
                      >
                         <option value="policy">Policy</option>
                         <option value="rule">Rule</option>
                         <option value="bio">Bio</option>
                         <option value="template">Template</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Tags (comma separated)</label>
                      <input 
                        value={newDoc.tags}
                        onChange={e => setNewDoc({...newDoc, tags: e.target.value})}
                        className="w-full px-6 py-4 rounded-xl border border-zinc-100 dark:border-gray-800 bg-zinc-50 dark:bg-gray-800 focus:outline-none focus:border-blue-500 font-bold"
                        placeholder="e.g. triage, urgent, emergency"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                     <label className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Intelligence Payload</label>
                     <textarea 
                       required
                       rows={6}
                       value={newDoc.content}
                       onChange={e => setNewDoc({...newDoc, content: e.target.value})}
                       className="w-full px-6 py-4 rounded-xl border border-zinc-100 dark:border-gray-800 bg-zinc-50 dark:bg-gray-800 focus:outline-none focus:border-blue-500 font-bold"
                       placeholder="Enter full clinical content or policy text..."
                     />
                  </div>
                  <button className="w-full bg-black dark:bg-blue-600 text-white py-6 rounded-xl font-black text-xs uppercase tracking-widest flex items-center justify-center gap-4 hover:bg-blue-700 transition-all shadow-2xl">
                     <Save size={18} /> Commit Node to Memory
                  </button>
               </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
