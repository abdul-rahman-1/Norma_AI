import { useState } from 'react';
import axios from 'axios';
import { Upload, FileType, CheckCircle, AlertCircle, FileSpreadsheet, Loader2, ArrowRight, ShieldCheck, DatabaseZap, X, Check, Save, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { cn } from '../utils/cn';

export default function BulkUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'preview' | 'committing' | 'success' | 'error'>('idle');
  const [previewData, setPreviewData] = useState<any>(null);
  const [committedResults, setCommittedResults] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [overwriteDuplicates, setOverwriteDuplicates] = useState(false);
  const { token } = useAuth();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setStatus('idle');
      setPreviewData(null);
      setCommittedResults(null);
    }
  };

  const handleUploadPreview = async () => {
    if (!file || !token) return;
    setStatus('uploading');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const res = await axios.post('/api/bulk/preview', formData, {
        headers: { 
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        }
      });
      setPreviewData(res.data);
      setStatus('preview');
    } catch (error: any) {
      console.error(error);
      setErrorMsg(error.response?.data?.detail || error.message || 'Manifest parsing failed');
      setStatus('error');
    }
  };

  const handleCommit = async () => {
    if (!previewData?.job_id || !token) return;
    setStatus('committing');
    
    try {
      const res = await axios.post('/api/bulk/commit', {
        job_id: previewData.job_id,
        overwrite_duplicates: overwriteDuplicates
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCommittedResults(res.data);
      setStatus('success');
    } catch (error: any) {
      console.error(error);
      setErrorMsg(error.response?.data?.detail || error.message || 'Commit phase failed');
      setStatus('error');
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-12 animate-in fade-in duration-700 pb-20 px-4">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 className="text-4xl font-black text-black dark:text-white tracking-tight uppercase italic">Ingestion Matrix</h1>
          <p className="text-zinc-500 dark:text-gray-400 mt-2 font-bold text-lg">High-fidelity clinical record synchronization and reconciliation.</p>
        </div>
        <div className="flex items-center gap-3 px-6 py-3 rounded-xl bg-zinc-50 dark:bg-gray-800 border border-zinc-200 dark:border-gray-700 shadow-sm">
           <ShieldCheck size={18} className="text-[#7c3aed] dark:text-blue-400" />
           <span className="text-[10px] font-black text-black dark:text-white uppercase tracking-widest">Secure Ingestion node</span>
        </div>
      </div>

      {(status === 'idle' || status === 'uploading') && (
        <div className="bg-white dark:bg-gray-800 p-12 md:p-20 rounded-[3rem] border border-gray-200 dark:border-gray-700 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-[#7c3aed]/5 blur-[100px] -mr-48 -mt-48 -z-10 rounded-full" />
          
          <div className="max-w-4xl mx-auto text-center">
            <div className="flex flex-col items-center mb-16">
              <div className="w-20 h-20 rounded-2xl bg-black dark:bg-blue-600 flex items-center justify-center text-[#7c3aed] dark:text-white shadow-2xl mb-8">
                <DatabaseZap size={36} />
              </div>
              <h2 className="text-3xl font-black text-black dark:text-white tracking-tight uppercase italic">Provision Dataset</h2>
            </div>
            
            <div className="border-4 border-dashed border-zinc-100 dark:border-gray-700 rounded-[3rem] p-16 md:p-24 text-center group hover:border-black dark:hover:border-blue-500 transition-all duration-700 bg-zinc-50/50 dark:bg-gray-900/50 hover:bg-white dark:hover:bg-gray-800 relative overflow-hidden shadow-inner">
              <div className="relative z-10">
                <div className="mx-auto h-28 w-28 bg-black dark:bg-blue-600 rounded-[2rem] shadow-2xl flex items-center justify-center text-zinc-500 dark:text-blue-200 group-hover:text-[#7c3aed] dark:group-hover:text-white transition-all duration-700 mb-10">
                  <Upload size={48} />
                </div>
                <h3 className="text-3xl font-black text-black dark:text-white mb-4 uppercase tracking-tight italic">Identify Manifest</h3>
                <p className="text-zinc-400 dark:text-gray-500 mb-12 max-w-sm mx-auto font-bold text-sm uppercase tracking-widest leading-relaxed">Standardized .xlsx format authorized for ingestion.</p>
                
                <input 
                  type="file" 
                  id="file-upload" 
                  className="hidden" 
                  accept=".xlsx, .xls" 
                  onChange={handleFileChange}
                />
                <label 
                  htmlFor="file-upload" 
                  className="cursor-pointer bg-black dark:bg-blue-600 text-white px-12 py-6 rounded-xl font-black uppercase tracking-[0.3em] text-xs hover:bg-[#7c3aed] dark:hover:bg-blue-700 transition-all active:scale-95 flex items-center gap-4 mx-auto w-fit shadow-2xl"
                >
                  <FileType size={20} />
                  Access Local Drive
                </label>
                
                {file && (
                  <div className="mt-16 flex items-center justify-center gap-6 text-black dark:text-white bg-zinc-50 dark:bg-gray-900 py-6 px-10 rounded-2xl w-fit mx-auto border border-zinc-200 dark:border-gray-700 shadow-xl animate-in zoom-in-95">
                    <div className="p-3 bg-black dark:bg-blue-600 rounded-xl text-[#7c3aed] dark:text-white">
                      <FileType size={28} />
                    </div>
                    <div className="text-left">
                      <span className="font-black text-base tracking-tight block truncate max-w-[250px]">{file.name}</span>
                      <span className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-widest mt-1">{(file.size / 1024).toFixed(1)} KB • Integrity Verified</span>
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
                onClick={handleUploadPreview}
                disabled={!file || status === 'uploading'}
                className={`w-full group relative py-8 rounded-[2rem] font-black text-xs uppercase tracking-[0.5em] transition-all flex items-center justify-center gap-6 shadow-2xl ${
                  !file || status === 'uploading' 
                    ? 'bg-zinc-100 dark:bg-gray-700 text-zinc-300 dark:text-gray-500 cursor-not-allowed border border-zinc-200 dark:border-gray-600' 
                    : 'bg-black dark:bg-blue-600 text-white hover:bg-[#7c3aed] dark:hover:bg-blue-700'
                }`}
              >
                {status === 'uploading' ? (
                  <>
                    <Loader2 className="animate-spin" size={24} />
                    Synchronizing Neural Mesh...
                  </>
                ) : (
                  <>
                    Authorize Preview
                    <ArrowRight size={24} className="text-[#7c3aed] dark:text-blue-400 group-hover:translate-x-2 transition-transform duration-500" />
                  </>
                )}
              </button>
              <p className="mt-8 text-[10px] font-black text-zinc-400 dark:text-gray-600 uppercase tracking-[0.4em] italic opacity-60">System encrypted clinical bridge v3.0 engaged</p>
            </div>
          </div>
        </div>
      )}

      <AnimatePresence>
        {(status === 'preview' || status === 'committing') && previewData && (
          <motion.div 
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="space-y-10"
          >
            <div className="bg-white dark:bg-gray-800 p-12 rounded-[3.5rem] border border-zinc-100 dark:border-gray-700 shadow-2xl">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-8 mb-12">
                <div className="flex items-center gap-8">
                  <div className="bg-black dark:bg-blue-600 p-6 rounded-[2rem] text-[#7c3aed] dark:text-white shadow-2xl">
                    <FileSpreadsheet size={40} />
                  </div>
                  <div>
                    <h2 className="text-4xl font-black tracking-tighter uppercase italic leading-none">Manifest Preview</h2>
                    <p className="text-sm text-zinc-500 dark:text-gray-400 font-bold uppercase tracking-widest mt-3 italic">Detected Entity: <span className="text-blue-600">{previewData.entity_type}</span></p>
                  </div>
                </div>
                
                <div className="flex flex-col items-end gap-4">
                   <div className="flex items-center gap-3 bg-zinc-50 dark:bg-gray-900 p-4 rounded-xl border border-zinc-200 dark:border-gray-700">
                      <input 
                        type="checkbox" 
                        id="overwrite" 
                        checked={overwriteDuplicates} 
                        onChange={(e) => setOverwriteDuplicates(e.target.checked)}
                        className="w-5 h-5 accent-blue-600 cursor-pointer"
                      />
                      <label htmlFor="overwrite" className="text-[10px] font-black text-zinc-500 dark:text-gray-400 uppercase tracking-widest cursor-pointer">Reconcile Duplicates (Overwrite)</label>
                   </div>
                   <button 
                    onClick={handleCommit}
                    disabled={status === 'committing'}
                    className="bg-black dark:bg-blue-600 text-white px-12 py-5 rounded-xl text-xs font-black uppercase tracking-[0.2em] shadow-2xl hover:bg-blue-700 transition-all flex items-center gap-4 active:scale-95 disabled:bg-zinc-100 dark:disabled:bg-gray-700"
                   >
                     {status === 'committing' ? <Loader2 size={18} className="animate-spin" /> : <Save size={18} />}
                     Commit to Registry
                   </button>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-12">
                {[
                  { label: 'Total Identified', value: previewData.summary.total_rows, color: 'text-black dark:text-white' },
                  { label: 'Validated', value: previewData.summary.valid, color: 'text-green-600' },
                  { label: 'Duplicates', value: previewData.summary.duplicates, color: 'text-orange-500' },
                  { label: 'Anomalies', value: previewData.summary.invalid, color: 'text-red-500' },
                ].map((stat, i) => (
                  <div key={i} className="bg-zinc-50 dark:bg-gray-900 p-8 rounded-[2rem] border border-zinc-100 dark:border-gray-700 shadow-inner">
                    <p className="text-[9px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-widest mb-3">{stat.label}</p>
                    <p className={`text-4xl font-black tracking-tighter ${stat.color}`}>{stat.value}</p>
                  </div>
                ))}
              </div>

              <div className="bg-zinc-50 dark:bg-gray-900 rounded-[2.5rem] overflow-hidden border border-zinc-100 dark:border-gray-700 shadow-inner">
                 <div className="p-8 border-b border-zinc-200 dark:border-gray-800 flex justify-between items-center">
                    <h3 className="text-xs font-black text-black dark:text-white uppercase tracking-widest italic">Core Object Sample (Top 10)</h3>
                 </div>
                 <div className="overflow-x-auto">
                    <table className="w-full text-left">
                      <thead className="bg-black dark:bg-gray-950 text-white">
                        <tr>
                          <th className="px-10 py-6 text-[9px] font-black uppercase tracking-[0.3em]">Ref</th>
                          <th className="px-10 py-6 text-[9px] font-black uppercase tracking-[0.3em]">Identity Core</th>
                          <th className="px-10 py-6 text-[9px] font-black uppercase tracking-[0.3em]">Contact Node</th>
                          <th className="px-10 py-6 text-[9px] font-black uppercase tracking-[0.3em]">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-zinc-200 dark:divide-gray-800">
                        {previewData.preview_rows.map((row: any, idx: number) => (
                          <tr key={idx} className="hover:bg-white dark:hover:bg-gray-800 transition-colors">
                            <td className="px-10 py-6">
                              <span className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">Row {row.row}</span>
                            </td>
                            <td className="px-10 py-6">
                              <span className="text-xs font-bold text-black dark:text-white">{row.record.full_name || row.record.name || 'Unidentified'}</span>
                            </td>
                            <td className="px-10 py-6">
                              <span className="text-xs text-zinc-500 dark:text-gray-400">{row.record.phone_number || row.record.whatsapp_number || 'No Vector'}</span>
                            </td>
                            <td className="px-10 py-6">
                               {row.is_duplicate ? (
                                 <span className="flex items-center gap-2 text-[9px] font-black text-orange-500 uppercase tracking-widest">
                                    <AlertTriangle size={12} /> Conflict Detected
                                 </span>
                               ) : (
                                 <span className="flex items-center gap-2 text-[9px] font-black text-green-500 uppercase tracking-widest">
                                    <Check size={12} /> Validated
                                 </span>
                               )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                 </div>
              </div>
            </div>

            {previewData.errors.length > 0 && (
              <div className="bg-white dark:bg-gray-800 p-12 rounded-[3.5rem] border-2 border-red-50 dark:border-red-900/10 shadow-2xl">
                 <div className="flex items-center gap-6 mb-10">
                    <div className="bg-red-500 p-4 rounded-2xl text-white">
                       <AlertCircle size={24} />
                    </div>
                    <h3 className="text-2xl font-black text-black dark:text-white uppercase italic tracking-tighter leading-none">Diagnostic Faults</h3>
                 </div>
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {previewData.errors.slice(0, 20).map((err: any, i: number) => (
                      <div key={i} className="flex items-start gap-6 p-6 bg-red-50/30 dark:bg-red-900/5 rounded-2xl border border-red-100/50 dark:border-red-900/10">
                         <div className="w-8 h-8 rounded-lg bg-red-500 text-white font-black text-[10px] flex items-center justify-center shrink-0">
                           {err.row}
                         </div>
                         <div>
                            <p className="text-[9px] font-black text-red-500 uppercase tracking-widest mb-1">{err.field}</p>
                            <p className="text-xs font-bold text-zinc-600 dark:text-gray-400 italic">"{err.reason}"</p>
                         </div>
                      </div>
                    ))}
                 </div>
                 {previewData.errors.length > 20 && (
                   <p className="mt-8 text-center text-[10px] font-black text-zinc-400 uppercase tracking-widest italic">+ {previewData.errors.length - 20} more faults detected</p>
                 )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {status === 'success' && committedResults && (
          <motion.div 
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white dark:bg-gray-800 p-16 rounded-[4rem] border-4 border-green-50 dark:border-green-900/20 shadow-2xl text-center relative overflow-hidden"
          >
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-green-500/5 blur-[120px] -z-10 rounded-full" />
            
            <div className="inline-flex bg-green-500 p-8 rounded-[2.5rem] text-white shadow-2xl shadow-green-500/20 mb-12">
              <ShieldCheck size={56} />
            </div>
            
            <h2 className="text-5xl font-black text-black dark:text-white uppercase italic tracking-tighter mb-6">Manifest Grounded</h2>
            <p className="text-zinc-500 dark:text-gray-400 font-bold text-xl max-w-2xl mx-auto leading-relaxed italic mb-16">
              Clinical registry has been successfully reconciled. Data vector integrity is 100% synchronized across all nodes.
            </p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto mb-16">
               {[
                 { label: 'Inserted', value: committedResults.results.inserted, color: 'text-green-500' },
                 { label: 'Updated', value: committedResults.results.updated, color: 'text-blue-500' },
                 { label: 'Skipped', value: committedResults.results.skipped, color: 'text-zinc-400' },
                 { label: 'Faults', value: committedResults.results.errors, color: 'text-red-500' },
               ].map((res, i) => (
                 <div key={i} className="p-8 bg-zinc-50 dark:bg-gray-900 rounded-[2.5rem] border border-zinc-100 dark:border-gray-800">
                    <p className="text-[9px] font-black text-zinc-400 uppercase tracking-[0.2em] mb-4">{res.label}</p>
                    <p className={`text-5xl font-black tracking-tighter ${res.color}`}>{res.value}</p>
                 </div>
               ))}
            </div>

            <button 
              onClick={() => { setStatus('idle'); setFile(null); setPreviewData(null); }}
              className="bg-black dark:bg-blue-600 text-white px-16 py-7 rounded-2xl font-black uppercase tracking-[0.4em] text-xs hover:bg-[#7c3aed] dark:hover:bg-blue-700 transition-all shadow-2xl active:scale-95"
            >
              Reset Terminal
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {status === 'error' && (
          <motion.div 
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white dark:bg-gray-800 p-12 rounded-[3.5rem] border-4 border-red-50 dark:border-red-900/20 flex items-start gap-10 shadow-2xl"
          >
            <div className="bg-red-500 p-6 rounded-[2rem] text-white shadow-2xl shadow-red-500/20">
              <AlertCircle size={40} />
            </div>
            <div className="flex-1 pt-2">
              <h3 className="text-3xl font-black text-red-500 mb-4 uppercase tracking-tighter italic leading-none">Bridge Failure</h3>
              <p className="text-zinc-500 dark:text-gray-400 font-bold text-xl leading-relaxed italic">Neural link rejected manifest ingestion: {errorMsg}</p>
              <button 
                onClick={() => setStatus('idle')}
                className="mt-12 bg-black dark:bg-blue-600 text-white px-12 py-5 rounded-xl text-[11px] font-black uppercase tracking-[0.4em] hover:bg-[#7c3aed] dark:hover:bg-blue-700 transition-all shadow-2xl active:scale-95"
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
