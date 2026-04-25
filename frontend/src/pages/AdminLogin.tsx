import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Activity, Lock, User, AlertCircle, ArrowRight, ShieldCheck, Sparkles, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

export default function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('norma_admin');
  const [password, setPassword] = useState('norma2026');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await axios.post('http://localhost:5000/api/auth/admin-login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('role', res.data.role);
      
      navigate('/admin-dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid admin credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white relative overflow-hidden p-6 font-premium">
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-black/5 blur-[120px] rounded-full -mr-32 -mt-32 -z-10" />

      <div className="w-full max-w-[1100px] grid grid-cols-1 lg:grid-cols-2 bg-white rounded-[2.5rem] shadow-[0_40px_100px_rgba(0,0,0,0.1)] border border-zinc-100 overflow-hidden min-h-[700px] relative z-10">
        <div className="hidden lg:flex flex-col justify-between bg-[#7c3aed] p-16 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-10 opacity-10">
             <ShieldCheck size={350} className="text-white" />
          </div>
          
          <div className="relative z-10 text-white">
            <div className="flex items-center gap-4 mb-16">
              <div className="bg-black text-white p-3 rounded-xl shadow-2xl">
                <ShieldCheck size={32} />
              </div>
              <span className="text-2xl font-black text-white italic tracking-tighter uppercase">NORMA AI</span>
            </div>
            
            <h2 className="text-7xl font-black text-white tracking-tighter leading-[0.9] uppercase mb-10 italic">
              Admin<br />
              <span className="text-black">Authority</span>
            </h2>
            <p className="text-white/70 text-xl font-medium leading-relaxed max-w-sm">
              Root level access terminal. Restricted to system administrators only. Unauthorized access is logged.
            </p>
          </div>

          <div className="relative z-10 flex items-center gap-6">
            <p className="text-[10px] font-black text-white/50 uppercase tracking-[0.25em] leading-tight">
              Root Level Terminal<br /><span className="text-black font-black">Secure Auth Protocol v3</span>
            </p>
          </div>
        </div>

        <div className="p-12 md:p-24 flex flex-col justify-center relative bg-white">
          <div className="mb-16">
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-zinc-50 border border-zinc-200 mb-8">
              <Lock size={16} className="text-[#7c3aed]" />
              <span className="text-[10px] font-black tracking-[0.3em] text-black uppercase">Admin Portal</span>
            </div>
            <h3 className="text-5xl font-black text-black tracking-tighter uppercase italic leading-none">Access</h3>
            <p className="text-zinc-400 font-bold text-xs uppercase tracking-[0.4em] mt-4 opacity-60">System identity required...</p>
          </div>
          
          {error && (
            <motion.div 
              initial={{ x: -10, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              className="bg-red-50 border border-red-100 p-5 rounded-xl mb-10 flex items-center gap-4 text-red-500 text-sm font-bold"
            >
              <AlertCircle size={20} />
              {error}
            </motion.div>
          )}

          <form onSubmit={handleLogin} className="space-y-10">
            <div className="space-y-4">
              <label className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.3em] ml-2">Admin ID</label>
              <div className="relative group">
                <User size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 group-focus-within:text-[#7c3aed] transition-colors" />
                <input 
                  type="text" 
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-zinc-50 border-2 border-transparent text-black pl-16 pr-8 py-6 rounded-xl text-lg font-black tracking-tight outline-none focus:bg-white focus:border-black transition-all shadow-inner"
                  placeholder="Admin Username..."
                  required
                />
              </div>
            </div>
            
            <div className="space-y-4">
              <label className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.3em] ml-2">Security Key</label>
              <div className="relative group">
                <Lock size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 group-focus-within:text-[#7c3aed] transition-colors" />
                <input 
                  type="password" 
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-zinc-50 border-2 border-transparent text-black pl-16 pr-8 py-6 rounded-xl text-lg font-black tracking-tight outline-none focus:bg-white focus:border-black transition-all shadow-inner"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>
            
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-black text-white py-8 rounded-xl font-black uppercase tracking-[0.4em] text-xs hover:bg-[#7c3aed] transition-all active:scale-95 shadow-2xl shadow-zinc-900/10 mt-6"
            >
              {loading ? (
                <Loader2 className="animate-spin mx-auto" size={24} />
              ) : (
                <div className="flex items-center justify-center gap-4">
                  <span>Authorize Access</span>
                  <ArrowRight size={20} className="text-[#7c3aed]" />
                </div>
              )}
            </button>
          </form>

          <div className="mt-20 text-center">
            <div className="flex items-center justify-center gap-5 opacity-20 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-1000">
              <Sparkles size={18} className="text-[#7c3aed]" />
              <p className="text-[10px] text-zinc-500 font-black uppercase tracking-[0.5em]">Global Control Sync</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
