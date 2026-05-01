import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion } from 'framer-motion';
import { Stethoscope, User, Phone, Mail, Award, DollarSign, FileText, ArrowLeft, CheckCircle2, Loader2, Sparkles } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function AddDoctor() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    whatsapp_number: '',
    specialty: '',
    license_number: '',
    email: '',
    phone: '',
    consultation_fee: 0,
    bio: ''
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setLoading(true);
    try {
      await axios.post('/api/doctors', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSuccess(true);
      setTimeout(() => navigate('/doctors'), 2000);
    } catch (err: any) {
      console.error('Failed to add doctor', err);
      alert(err.response?.data?.detail || 'Failed to add doctor. Ensure you have admin permissions.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-12 px-6">
      <button 
        onClick={() => navigate(-1)}
        className="flex items-center gap-3 text-zinc-500 hover:text-black dark:text-gray-400 dark:hover:text-white transition-colors mb-12 group"
      >
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        <span className="text-[10px] font-black uppercase tracking-[0.3em]">Back to Terminal</span>
      </button>

      <div className="bg-white dark:bg-gray-800 rounded-[3rem] p-12 shadow-[0_50px_100px_rgba(0,0,0,0.05)] border border-zinc-100 dark:border-gray-700 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-12 opacity-[0.03] dark:opacity-[0.05] pointer-events-none">
          <Stethoscope size={300} className="dark:text-white" />
        </div>

        <div className="relative z-10">
          <header className="mb-16">
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-[#7c3aed]/5 border border-[#7c3aed]/10 mb-8">
              <Sparkles size={16} className="text-[#7c3aed]" />
              <span className="text-[10px] font-black tracking-[0.3em] text-[#7c3aed] uppercase">New Medical Node</span>
            </div>
            <h1 className="text-5xl font-black text-black dark:text-white tracking-tighter uppercase italic leading-none">Register Doctor</h1>
            <p className="text-zinc-400 dark:text-gray-500 font-bold text-xs uppercase tracking-[0.4em] mt-4 opacity-60">Initializing specialist profile...</p>
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
              <h2 className="text-3xl font-black text-black dark:text-white uppercase italic tracking-tighter">Registration Complete</h2>
              <p className="text-zinc-500 dark:text-gray-400 font-bold uppercase tracking-widest text-[10px]">Syncing to distributed ledger...</p>
            </motion.div>
          ) : (
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-[0.3em] ml-2">Full Name</label>
                <div className="relative group">
                  <User size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 dark:text-gray-600 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="text" 
                    required
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-black dark:focus:border-blue-500 transition-all"
                    placeholder="Dr. Name..."
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-[0.3em] ml-2">Specialty</label>
                <div className="relative group">
                  <Award size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 dark:text-gray-600 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="text" 
                    required
                    value={formData.specialty}
                    onChange={(e) => setFormData({...formData, specialty: e.target.value})}
                    className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-black dark:focus:border-blue-500 transition-all"
                    placeholder="Cardiology, etc..."
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-[0.3em] ml-2">WhatsApp Number</label>
                <div className="relative group">
                  <Phone size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 dark:text-gray-600 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="text" 
                    required
                    value={formData.whatsapp_number}
                    onChange={(e) => setFormData({...formData, whatsapp_number: e.target.value})}
                    className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-black dark:focus:border-blue-500 transition-all"
                    placeholder="+1234567890"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-[0.3em] ml-2">License Number</label>
                <div className="relative group">
                  <FileText size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 dark:text-gray-600 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="text" 
                    value={formData.license_number}
                    onChange={(e) => setFormData({...formData, license_number: e.target.value})}
                    className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-black dark:focus:border-blue-500 transition-all"
                    placeholder="MD-123456"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-[0.3em] ml-2">Email Address</label>
                <div className="relative group">
                  <Mail size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 dark:text-gray-600 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="email" 
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-black dark:focus:border-blue-500 transition-all"
                    placeholder="doctor@clinic.com"
                  />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-[0.3em] ml-2">Consultation Fee</label>
                <div className="relative group">
                  <DollarSign size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300 dark:text-gray-600 group-focus-within:text-[#7c3aed] transition-colors" />
                  <input 
                    type="number" 
                    value={formData.consultation_fee}
                    onChange={(e) => setFormData({...formData, consultation_fee: parseFloat(e.target.value)})}
                    className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white pl-16 pr-8 py-5 rounded-2xl text-sm font-black tracking-tight outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-black dark:focus:border-blue-500 transition-all"
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div className="md:col-span-2 space-y-4">
                <label className="text-[10px] font-black text-zinc-400 dark:text-gray-500 uppercase tracking-[0.3em] ml-2">Professional Bio</label>
                <textarea 
                  value={formData.bio}
                  onChange={(e) => setFormData({...formData, bio: e.target.value})}
                  rows={4}
                  className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-8 py-5 rounded-3xl text-sm font-black tracking-tight outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-black dark:focus:border-blue-500 transition-all resize-none"
                  placeholder="Tell us about the doctor's background..."
                />
              </div>

              <div className="md:col-span-2 pt-6">
                <button 
                  type="submit" 
                  disabled={loading}
                  className="w-full bg-black dark:bg-blue-600 text-white py-6 rounded-2xl font-black uppercase tracking-[0.4em] text-[10px] hover:bg-[#7c3aed] dark:hover:bg-blue-700 transition-all active:scale-[0.98] shadow-2xl shadow-zinc-900/10"
                >
                  {loading ? (
                    <Loader2 className="animate-spin mx-auto" size={20} />
                  ) : (
                    "Authorize Specialist Registration"
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
