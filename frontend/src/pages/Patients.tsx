import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Users, Search, Plus, MoreVertical, Edit2, Trash2, Loader2, X,
  Phone, User, MapPin, FileText, Mail, Calendar, Languages, ShieldCheck, AlertCircle,
  ArrowUpRight, Filter, Fingerprint
} from 'lucide-react';
import { cn } from '../utils/cn';

export default function Patients() {
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingPatient, setEditingDoctor] = useState<any>(null);
  
  const initialForm = {
    full_name: '',
    phone_number: '',
    email: '',
    gender: 'Other',
    address: '',
    notes: '',
    preferred_language: 'ar'
  };
  
  const [formData, setFormData] = useState(initialForm);
  const [activeMenu, setActiveMenu] = useState<string | null>(null);

  const fetchPatients = async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await axios.get('http://localhost:5000/api/patients', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPatients(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    setError('');

    try {
      if (editingPatient) {
        await axios.patch(`http://localhost:5000/api/patients/${editingPatient._id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('http://localhost:5000/api/patients', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setShowModal(false);
      setEditingDoctor(null);
      setFormData(initialForm);
      fetchPatients();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'System rejected the entry. Verify clinical credentials.');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('De-authorize this patient record?')) return;
    const token = localStorage.getItem('token');
    try {
      await axios.delete(`http://localhost:5000/api/patients/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchPatients();
    } catch (err) {
      console.error(err);
    }
  };

  const filteredPatients = patients.filter(p => 
    p.full_name?.toLowerCase().includes(search.toLowerCase()) || 
    p.phone_number?.includes(search)
  );

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center">
        <Loader2 className="animate-spin text-violet-600" size={40} />
      </div>
    );
  }

  return (
    <div className="space-y-12 animate-in fade-in duration-1000 pb-20">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6">
        <div>
          <h1 className="text-4xl font-black text-slate-900 tracking-tight uppercase">Patient Registry</h1>
          <p className="text-slate-500 mt-2 font-medium text-lg italic">Autonomous patient identity and clinical profile management.</p>
        </div>
        <button 
          onClick={() => { setEditingDoctor(null); setFormData(initialForm); setError(''); setShowModal(true); }}
          className="group bg-slate-900 text-white px-10 py-5 rounded-[2rem] text-sm font-black shadow-2xl hover:bg-violet-600 transition-all flex items-center gap-4 active:scale-95"
        >
          <Plus size={20} className="text-violet-400 group-hover:rotate-90 transition-transform duration-500" /> 
          Register Patient
        </button>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        <div className="flex-1 nm-inset p-5 rounded-[1.8rem] border border-white flex items-center gap-5 focus-within:ring-4 focus-within:ring-violet-500/5 focus-within:border-violet-200 transition-all">
          <Search size={22} className="text-slate-300 ml-3" />
          <input 
            type="text" 
            placeholder="Identify patient by name or neural contact code..." 
            className="bg-transparent border-none outline-none text-slate-900 w-full py-2 font-bold text-sm placeholder-slate-300"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button className="nm-button px-8 py-5 rounded-[1.8rem] text-slate-400 font-black text-[10px] uppercase tracking-[0.3em] flex items-center gap-3 hover:text-violet-600 transition-all">
          <Filter size={18} />
          Refine Mesh
        </button>
      </div>

      <div className="nm-luxury rounded-[3.5rem] border border-white overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="bg-slate-50/50">
                <th className="px-10 py-8 text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Patient Identity</th>
                <th className="px-10 py-8 text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Neural Axis</th>
                <th className="px-10 py-8 text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Temporal Info</th>
                <th className="px-10 py-8 text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">System Rank</th>
                <th className="px-10 py-8"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {filteredPatients.map((patient) => (
                <tr key={patient._id} className="hover:bg-slate-50/80 transition-all group">
                  <td className="px-10 py-8">
                    <div className="flex items-center gap-5">
                      <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-xs font-black text-violet-400 shadow-xl group-hover:scale-105 transition-transform duration-500">
                        {patient.full_name?.split(' ').map((n: any) => n[0]).join('') || 'P'}
                      </div>
                      <div>
                        <p className="text-base font-black text-slate-900 group-hover:text-violet-600 transition-colors tracking-tight">{patient.full_name}</p>
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mt-1 opacity-60">#{patient.patient_uuid?.slice(0, 8)}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-10 py-8">
                    <p className="text-sm font-black text-slate-900 flex items-center gap-2">
                       <Phone size={14} className="text-violet-400" />
                       {patient.phone_number}
                    </p>
                    <p className="text-[10px] text-slate-400 font-bold tracking-tight mt-1 lowercase italic">{patient.email || 'no-neural-mail'}</p>
                  </td>
                  <td className="px-10 py-8">
                    <p className="text-sm font-black text-slate-900">{patient.gender}</p>
                    <p className="text-[10px] text-slate-400 font-bold tracking-tight mt-1 uppercase italic flex items-center gap-2">
                       <MapPin size={12} className="text-violet-400" />
                       {patient.address || 'Geo-Location Missing'}
                    </p>
                  </td>
                  <td className="px-10 py-8">
                    <div className="flex items-center gap-2.5 px-4 py-2 bg-white rounded-xl border border-slate-100 shadow-sm w-fit">
                       <ShieldCheck size={14} className="text-emerald-500" />
                       <span className="text-[9px] font-black text-slate-900 uppercase tracking-widest">Verified Resident</span>
                    </div>
                  </td>
                  <td className="px-10 py-8 text-right relative">
                    <button 
                      onClick={() => setActiveMenu(activeMenu === patient._id ? null : patient._id)}
                      className="text-slate-300 hover:text-violet-600 p-3 rounded-2xl nm-button shadow-none"
                    >
                      <MoreVertical size={24} />
                    </button>
                    
                    {activeMenu === patient._id && (
                      <div className="absolute right-16 top-1/2 -translate-y-1/2 bg-white border border-slate-100 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.1)] z-50 py-3 w-56 animate-in zoom-in-95 duration-300">
                        <button 
                          onClick={() => {
                            setEditingDoctor(patient);
                            setFormData({
                              full_name: patient.full_name,
                              phone_number: patient.phone_number,
                              email: patient.email || '',
                              gender: patient.gender,
                              address: patient.address || '',
                              notes: patient.notes || '',
                              preferred_language: patient.preferred_language || 'ar'
                            });
                            setShowModal(true);
                            setActiveMenu(null);
                          }}
                          className="w-full flex items-center justify-between px-6 py-3 text-sm font-black text-slate-900 hover:bg-violet-50 hover:text-violet-600 transition-all group/btn"
                        >
                          Modify Assets <ArrowUpRight size={16} className="text-slate-300 group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
                        </button>
                        <div className="h-[1px] bg-slate-50 my-1 mx-4" />
                        <button 
                          onClick={() => { handleDelete(patient._id); setActiveMenu(null); }}
                          className="w-full flex items-center justify-between px-6 py-3 text-sm font-black text-red-500 hover:bg-red-50 transition-all"
                        >
                          Erase Entry <Trash2 size={16} />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {filteredPatients.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-10 py-32 text-center">
                    <div className="flex flex-col items-center gap-4 opacity-30 grayscale scale-75">
                       <Users size={64} className="text-slate-400" />
                       <p className="text-lg font-bold text-slate-500 italic uppercase tracking-tighter">Clinical mesh empty. No patient nodes identified.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xl flex items-center justify-center z-[100] p-6">
          <div className="bg-white border border-slate-200 rounded-[3.5rem] w-full max-w-5xl shadow-[0_60px_120px_-20px_rgba(0,0,0,0.2)] overflow-hidden animate-in zoom-in-95 duration-700">
            <div className="p-12 md:p-16 border-b border-slate-50 flex justify-between items-center bg-slate-50/50">
              <div>
                <h2 className="text-4xl font-black text-slate-900 tracking-tighter uppercase leading-none">
                  {editingPatient ? 'Modify Profile' : 'Authorize Asset'}
                </h2>
                <p className="text-[10px] text-slate-400 font-black uppercase tracking-[0.4em] mt-4 italic">Neural Identity Registration Node</p>
              </div>
              <button onClick={() => setShowModal(false)} className="bg-white p-5 rounded-[1.8rem] text-slate-300 hover:text-red-500 border border-slate-100 hover:border-red-100 transition-all shadow-sm">
                <X size={32} />
              </button>
            </div>

            {error && (
              <div className="mx-12 mt-10 bg-red-50 border-2 border-red-100 p-6 rounded-[2rem] flex items-center gap-5 text-red-500 text-xs font-black uppercase tracking-widest animate-in shake duration-500 shadow-xl shadow-red-500/5">
                <AlertCircle size={24} />
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="p-12 md:p-16 grid grid-cols-2 gap-x-16 gap-y-10 overflow-y-auto max-h-[65vh] scrollbar-thin">
              {/* Profile Block */}
              <div className="col-span-2 flex items-center gap-6 mb-2">
                <span className="text-[11px] font-black text-violet-600 uppercase tracking-[0.4em] whitespace-nowrap italic">Profile Configuration</span>
                <div className="h-[2px] w-full bg-gradient-to-r from-violet-100 to-transparent" />
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Full Identity *</label>
                <div className="relative group">
                  <User size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within:text-violet-600 transition-colors" />
                  <input type="text" required placeholder="Legal Name..." className="w-full bg-slate-50 border-2 border-transparent text-slate-900 pl-16 pr-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner" value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Neural Contact *</label>
                <div className="relative group">
                  <Phone size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within:text-violet-600 transition-colors" />
                  <input type="text" required placeholder="E.164 Format..." className="w-full bg-slate-50 border-2 border-transparent text-slate-900 pl-16 pr-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner" value={formData.phone_number} onChange={e => setFormData({...formData, phone_number: e.target.value})} />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Digital Mail</label>
                <div className="relative group">
                  <Mail size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within:text-violet-600 transition-colors" />
                  <input type="email" placeholder="example@node.net" className="w-full bg-slate-50 border-2 border-transparent text-slate-900 pl-16 pr-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} />
                </div>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Genetic Marker</label>
                <div className="relative group">
                  <Fingerprint size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-300 group-focus-within:text-violet-600 transition-colors" />
                  <select className="w-full bg-slate-50 border-2 border-transparent text-slate-900 pl-16 pr-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner appearance-none" value={formData.gender} onChange={e => setFormData({...formData, gender: e.target.value})}>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div className="col-span-2 space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Clinical Observational Data</label>
                <div className="relative group">
                  <FileText size={20} className="absolute left-6 top-8 text-slate-300 group-focus-within:text-violet-600 transition-colors" />
                  <textarea rows={4} placeholder="Allergies, chronic markers, or system anomalies..." className="w-full bg-slate-50 border-2 border-transparent text-slate-900 pl-16 pr-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner resize-none" value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} />
                </div>
              </div>

              <div className="col-span-2 pt-10 flex gap-10">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-white text-slate-400 py-7 rounded-[2.2rem] font-black uppercase tracking-[0.3em] text-xs border-2 border-slate-100 hover:bg-slate-50 hover:text-slate-900 transition-all shadow-sm">Discard Asset</button>
                <button type="submit" className="flex-1 bg-slate-900 text-white py-7 rounded-[2.2rem] font-black uppercase tracking-[0.3em] text-xs shadow-2xl shadow-slate-900/20 hover:bg-violet-600 hover:-translate-y-1 transition-all active:scale-95">Commit Asset To Registry</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
