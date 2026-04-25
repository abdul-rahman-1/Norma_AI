import { useState } from 'react';
import axios from 'axios';
import { Upload, FileType, CheckCircle, AlertCircle, FileSpreadsheet, Loader2, ArrowRight, ShieldCheck, DatabaseZap, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function BulkUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [summary, setSummary] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus('idle');
      setSummary(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus('uploading');
    
    const token = localStorage.getItem('token');
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post('http://localhost:5000/api/uploads/excel', formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      setSummary(res.data.summary);
      setStatus('success');
    } catch (error: any) {
      console.error(error);
      setErrorMsg(error.response?.data?.detail || error.message || 'Data integration failed');
      setStatus('error');
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-12 animate-in fade-in duration-700 pb-20 px-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="text-4xl font-black text-black tracking-tight uppercase italic">Ingestion Matrix</h1>
          <p className="text-zinc-500 mt-2 font-bold text-lg">High-fidelity clinical record synchronization and reconciliation.</p>
        </div>
        <div className="flex items-center gap-3 px-6 py-3 rounded-xl bg-zinc-50 border border-zinc-200">
           <ShieldCheck size={18} className="text-[#7c3aed]" />
           <span className="text-[10px] font-black text-black uppercase tracking-widest">Secure Ingestion node</span>
        </div>
      </div>

      <div className="bg-white p-12 md:p-20 rounded-[3rem] border-2 border-zinc-50 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-[#7c3aed]/5 blur-[100px] -mr-48 -mt-48 -z-10 rounded-full" />
        
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex flex-col items-center mb-16">
            <div className="w-20 h-20 rounded-2xl bg-black flex items-center justify-center text-[#7c3aed] shadow-2xl mb-8">
              <DatabaseZap size={36} />
            </div>
            <h2 className="text-3xl font-black text-black tracking-tight uppercase italic">Provision Dataset</h2>
          </div>
          
          <div className="border-4 border-dashed border-zinc-100 rounded-[3rem] p-16 md:p-24 text-center group hover:border-black transition-all duration-700 bg-zinc-50/50 hover:bg-white relative overflow-hidden shadow-inner">
            <div className="relative z-10">
              <div className="mx-auto h-28 w-28 bg-black rounded-[2rem] shadow-2xl flex items-center justify-center text-zinc-500 group-hover:text-[#7c3aed] transition-all duration-700 mb-10">
                <Upload size={48} />
              </div>
              <h3 className="text-3xl font-black text-black mb-4 uppercase tracking-tight italic">Identify Manifest</h3>
              <p className="text-zinc-400 mb-12 max-w-sm mx-auto font-bold text-sm uppercase tracking-widest leading-relaxed">Standardized .xlsx format authorized for ingestion.</p>
              
              <input 
                type="file" 
                id="file-upload" 
                className="hidden" 
                accept=".xlsx, .xls" 
                onChange={handleFileChange}
              />
              <label 
                htmlFor="file-upload" 
                className="cursor-pointer bg-black text-white px-12 py-6 rounded-xl font-black uppercase tracking-[0.3em] text-xs hover:bg-[#7c3aed] transition-all active:scale-95 flex items-center gap-4 mx-auto w-fit shadow-2xl"
              >
                <FileType size={20} />
                Access Local Drive
              </label>
              
              {file && (
                <div className="mt-16 flex items-center justify-center gap-6 text-black bg-zinc-50 py-6 px-10 rounded-2xl w-fit mx-auto border border-zinc-200 shadow-xl animate-in zoom-in-95">
                  <div className="p-3 bg-black rounded-xl text-[#7c3aed]">
                    <FileType size={28} />
                  </div>
                  <div className="text-left">
                    <span className="font-black text-base tracking-tight block truncate max-w-[250px]">{file.name}</span>
                    <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mt-1">{(file.size / 1024).toFixed(1)} KB • Integrity Verified</span>
                  </div>
                  <button onClick={() => setFile(null)} className="ml-6 text-zinc-300 hover:text-red-500 transition-colors">
                    <X size={24} />
                  </button>
                </div>
              )}
            </div>
          </div>
          
          <div className="mt-16 flex flex-col items-center">
            <button
              onClick={handleUpload}
              disabled={!file || status === 'uploading'}
              className={`w-full group relative py-8 rounded-[2rem] font-black text-xs uppercase tracking-[0.5em] transition-all flex items-center justify-center gap-6 shadow-2xl ${
                !file || status === 'uploading' 
                  ? 'bg-zinc-100 text-zinc-300 cursor-not-allowed border border-zinc-200' 
                  : 'bg-black text-white hover:bg-[#7c3aed]'
              }`}
            >
              {status === 'uploading' ? (
                <>
                  <Loader2 className="animate-spin" size={24} />
                  Synchronizing Neural Mesh...
                </>
              ) : (
                <>
                  Authorize Ingestion
                  <ArrowRight size={24} className="text-[#7c3aed] group-hover:translate-x-2 transition-transform duration-500" />
                </>
              )}
            </button>
            <p className="mt-8 text-[10px] font-black text-zinc-400 uppercase tracking-[0.4em] italic opacity-60">System encrypted clinical bridge v3.0 engaged</p>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {status === 'success' && summary && (
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="bg-white p-12 md:p-16 rounded-[3.5rem] border-2 border-zinc-50 shadow-2xl relative overflow-hidden"
          >
            <div className="flex items-center gap-8 text-black mb-16 relative z-10">
              <div className="bg-black p-6 rounded-[2rem] text-[#7c3aed] shadow-2xl">
                <CheckCircle size={40} />
              </div>
              <div>
                <h2 className="text-4xl font-black tracking-tighter uppercase italic leading-none">Ingestion successful</h2>
                <p className="text-sm text-zinc-500 font-bold uppercase tracking-widest mt-3 italic">Clinical registry updated across all nodes</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-8 mb-16 relative z-10">
              {[
                { label: 'Total Identified', value: summary.total, color: 'text-black' },
                { label: 'New Identities', value: summary.inserted, color: 'text-[#7c3aed]' },
                { label: 'Reconciled', value: summary.skipped, color: 'text-zinc-400' },
                { label: 'Anomalies', value: summary.errors.length, color: 'text-red-500' },
              ].map((stat, i) => (
                <div key={i} className="bg-zinc-50 p-10 rounded-[2.5rem] flex flex-col border border-zinc-100 shadow-inner">
                  <p className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.2em] mb-4">{stat.label}</p>
                  <p className={`text-5xl font-black tracking-tighter ${stat.color}`}>{stat.value}</p>
                </div>
              ))}
            </div>

            {summary.errors.length > 0 && (
              <div className="space-y-8 relative z-10">
                <div className="flex items-center gap-4">
                  <AlertCircle size={24} className="text-red-500" />
                  <h3 className="font-black text-black uppercase tracking-widest text-sm italic">Anomaly Diagnostic Matrix</h3>
                </div>
                <div className="bg-zinc-50 rounded-[2.5rem] overflow-hidden border border-zinc-100 shadow-inner">
                  <table className="w-full text-left">
                    <thead className="bg-black text-white">
                      <tr>
                        <th className="px-10 py-8 text-[11px] font-black uppercase tracking-[0.3em]">Identity Reference</th>
                        <th className="px-10 py-8 text-[11px] font-black uppercase tracking-[0.3em]">Error Vector Description</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-200">
                      {summary.errors.map((err: any, idx: number) => (
                        <tr key={idx} className="hover:bg-white transition-colors">
                          <td className="px-10 py-8">
                            <span className="text-sm font-black uppercase italic">Row Object {err.row}</span>
                          </td>
                          <td className="px-10 py-8">
                            <span className="text-sm text-red-500 font-bold tracking-tight">{err.reason}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {status === 'error' && (
          <motion.div 
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white p-12 rounded-[3.5rem] border-4 border-red-50 flex items-start gap-10 shadow-2xl"
          >
            <div className="bg-red-500 p-6 rounded-[2rem] text-white shadow-2xl shadow-red-500/20">
              <AlertCircle size={40} />
            </div>
            <div className="flex-1 pt-2">
              <h3 className="text-3xl font-black text-red-500 mb-4 uppercase tracking-tighter italic leading-none">Bridge Failure</h3>
              <p className="text-zinc-500 font-bold text-xl leading-relaxed italic">Neural link rejected manifest ingestion: {errorMsg}</p>
              <button 
                onClick={() => setStatus('idle')}
                className="mt-12 bg-black text-white px-12 py-5 rounded-xl text-[11px] font-black uppercase tracking-[0.4em] hover:bg-[#7c3aed] transition-all shadow-2xl active:scale-95"
              >
                Abort & Initialize Retry
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
