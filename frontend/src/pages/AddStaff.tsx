import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Users, User, Phone, Mail, Lock, ArrowLeft, CheckCircle2, Loader2, Sparkles } from 'lucide-react';

export default function AddStaff() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    phone_number: '',
    email: '',
    password: '',
    role: 'receptionist'
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post('http://localhost:5000/api/auth/add-staff', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess(true);
      setTimeout(() => navigate('/admin-dashboard'), 2000);
    } catch (err) {
      console.error('Failed to add staff', err);
      alert('Failed to add staff. Ensure you have the required permissions.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-12 px-6">
      <button 
        onClick={() => navigate(-1)}
        className="flex items-center gap-3 text-zinc-500 hover:text-black transition-colors mb-12 group"
      >
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        <span className="text-[10px] font-black uppercase tracking-[0.3em]">Back to Terminal</span>
      </button>

      <div className="bg-white rounded-[3rem] p-12 shadow-[0_50px_100px_rgba(0,0,0,0.05)] border border-zinc-100 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-12 opacity-[0.03] pointer-events-none">
          <Users size={300} />
        </div>

        <div className="relative z-10">
          <header className="mb-16">
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-[#7c3aed]/5 border border-[#7c3aed]/10 mb-8">
              <Sparkles size={16} className="text-[#7c3aed]" />
              <span className="text-[10px] font-black tracking-[0.3em] text-[#7c3aed] uppercase">New Operator Node</span>
            </div>
            <h1 className="text-5xl font-black text-black tracking-tighter uppercase italic leading-none">Register Staff</h1>
            <p className="text-zinc-400 font-bold text-xs uppercase tracking-[0.4em] mt-4 opacity-60">Initializing personnel profile...</p>
          </header>

          {success ? (
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="py-20 flex flex-col items-center text-center space-y-6"
            >
              <div className="w-24 h-24 bg-green-500 text-white rounded-full flex items-center justify-center shadow-2xl shadow-green-500/20">
                <CheckCircle2 size={48} />
              </div>
              <h2 className="text-3xl font-black uppercase italic tracking-tighter">Staff Provisioned</h2>
              <p className="text-zinc-500 font-bold uppercase tracking-widest text-[10px]">Access credentials established...</p>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.3em] ml-2">Full Name</label>
                <div className="relative group">
                  <User size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="text" 
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full bg-zinc-50 border-2 border-transparent text-black pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white focus:border-black transition-all"
                    placeholder="Staff Member Name..."
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.3em] ml-2">Phone Number (Terminal ID)</label>
                <div className="relative group">
                  <Phone size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="text" 
                    required
                    value={formData.phone_number}
                    onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                    className="w-full bg-zinc-50 border-2 border-transparent text-black pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white focus:border-black transition-all"
                    placeholder="9876543210"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.3em] ml-2">Email Address</label>
                <div className="relative group">
                  <Mail size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="email" 
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full bg-zinc-50 border-2 border-transparent text-black pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white focus:border-black transition-all"
                    placeholder="staff@clinic.com"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.3em] ml-2">Access Key (Password)</label>
                <div className="relative group">
                  <Lock size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="password" 
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({...formData, password: e.target.value})}
                    className="w-full bg-zinc-50 border-2 border-transparent text-black pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white focus:border-black transition-all"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <div className="md:col-span-2 pt-6">
                <button 
                  type="submit" 
                  disabled={loading}
                  className="w-full bg-black text-white py-6 rounded-2xl font-black uppercase tracking-[0.4em] text-[10px] hover:bg-[#7c3aed] transition-all active:scale-[0.98] shadow-2xl shadow-zinc-900/10"
                >
                  {loading ? (
                    <Loader2 className="animate-spin mx-auto" size={20} />
                  ) : (
                    "Authorize Personnel Access"
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
