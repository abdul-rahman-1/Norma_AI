import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Loader2, Plus, Search, MoreHorizontal, Edit, Trash, X, AlertCircle, Phone, Mail, User as UserIcon, Calendar } from 'lucide-react';
import axios from 'axios';
import { cn } from '../utils/cn';

export default function Patients() {
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingPatient, setEditingPatient] = useState<any>(null);
  const { token, userRole } = useAuth();
  
  const initialForm = {
    full_name: '',
    phone_number: '',
    email: '',
    gender: 'Other',
    date_of_birth: '',
    address: '',
    insurance_provider: '',
    insurance_id: '',
    notes: ''
  };
  
  const [formData, setFormData] = useState(initialForm);

  const fetchPatients = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      const res = await axios.get('/api/patients', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPatients(res.data);
    } catch (err: any) { 
      setError(err.response?.data?.detail || err.message || "Failed to synchronize patient registry");
    } finally { 
      setLoading(false); 
    }
  }, [token]);

  useEffect(() => {
    fetchPatients();
  }, [fetchPatients]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const url = editingPatient ? `/api/patients/${editingPatient._id}` : '/api/patients';
    const method = editingPatient ? 'patch' : 'post';

    try {
      await axios({
        method,
        url,
        data: formData,
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowModal(false);
      fetchPatients();
    } catch (err: any) { 
      setError(err.response?.data?.detail || err.message || 'Sequence commit failed.');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Archive this patient record?')) return;
    try {
      await axios.delete(`/api/patients/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchPatients();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Archive failed.');
    }
  };

  const filteredPatients = patients.filter(p => 
    p.full_name?.toLowerCase().includes(search.toLowerCase()) || 
    p.phone_number?.includes(search) ||
    p.patient_uuid?.includes(search) ||
    p._id?.includes(search)
  );

  return (
    <div className="max-w-[1400px] mx-auto space-y-8 pb-20">
      <header className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6">
        <div>
          <h1 className="text-4xl font-black text-black dark:text-white tracking-tight uppercase italic">Registry</h1>
          <p className="text-zinc-500 mt-2 font-bold text-lg">Centralized clinical identity and health history management.</p>
        </div>
        <button 
          onClick={() => { setEditingPatient(null); setFormData(initialForm); setShowModal(true); }}
          className="group bg-black dark:bg-blue-600 text-white px-10 py-5 rounded-xl text-xs font-black uppercase tracking-[0.2em] shadow-2xl hover:bg-blue-700 transition-all flex items-center gap-4 active:scale-95"
        >
          <Plus size={18} className="text-white group-hover:rotate-90 transition-transform" /> 
          Register Identity
        </button>
      </header>

      {error && (
        <div className="p-6 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-2xl flex items-center gap-4 font-bold text-sm border border-red-100 dark:border-red-900/30 shadow-sm animate-in slide-in-from-top-4">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      <div className="relative group">
        <Search size={20} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-blue-500 transition-colors" />
        <input 
          type="text" 
          placeholder="Locate by Name, Phone, or Global ID..." 
          className="w-full h-16 pl-16 pr-6 bg-white dark:bg-gray-800 border-2 border-zinc-100 dark:border-gray-700 rounded-2xl text-base font-bold text-black dark:text-white outline-none focus:border-blue-500 transition-all shadow-sm"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-[2.5rem] border-2 border-zinc-50 dark:border-gray-700 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead>
              <tr className="text-[10px] font-black text-zinc-400 uppercase tracking-[0.2em] bg-zinc-50/50 dark:bg-gray-900/50 border-b border-zinc-50 dark:border-gray-700">
                <th scope="col" className="px-10 py-6">Clinical Identity</th>
                <th scope="col" className="px-10 py-6">Connectivity</th>
                <th scope="col" className="px-10 py-6">Status</th>
                <th scope="col" className="px-10 py-6">Enrolled</th>
                <th scope="col" className="px-10 py-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-50 dark:divide-gray-700">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-10 py-20">
                    <div className="flex flex-col items-center gap-4">
                      <Loader2 className="animate-spin text-blue-600" size={32} />
                      <p className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Syncing Registry...</p>
                    </div>
                  </td>
                </tr>
              ) : filteredPatients.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-10 py-20 text-center text-zinc-400 font-bold italic">
                    Registry empty. No matching identities identified.
                  </td>
                </tr>
              ) : filteredPatients.map((patient) => (
                <tr key={patient._id} className="hover:bg-zinc-50/50 dark:hover:bg-gray-900/30 transition-colors group">
                  <td className="px-10 py-6">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-zinc-100 dark:bg-gray-700 flex items-center justify-center text-zinc-400 font-black">
                        {patient.full_name?.charAt(0)}
                      </div>
                      <div>
                        <p className="text-lg font-black text-black dark:text-white leading-tight">{patient.full_name}</p>
                        <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mt-1">ID: {patient.patient_uuid?.split('-')[0] || 'N/A'}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-10 py-6">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-zinc-500 dark:text-gray-400 font-bold">
                        <Phone size={14} className="text-blue-500" />
                        <span>{patient.phone_number}</span>
                      </div>
                      {patient.email && (
                        <div className="flex items-center gap-2 text-zinc-400 text-xs font-medium italic">
                          <Mail size={14} />
                          <span>{patient.email}</span>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-10 py-6">
                    <span className={cn(
                      "px-4 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest border",
                      patient.is_active !== false ? "bg-green-50 text-green-600 border-green-100" : "bg-zinc-100 text-zinc-400 border-zinc-200"
                    )}>
                      {patient.is_active !== false ? "Active" : "Archived"}
                    </span>
                  </td>
                  <td className="px-10 py-6 text-zinc-400 font-bold text-xs uppercase">
                    {patient.created_at ? new Date(patient.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A'}
                  </td>
                  <td className="px-10 py-6 text-right">
                    <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button 
                        onClick={() => { setEditingPatient(patient); setFormData({...patient}); setShowModal(true); }}
                        className="p-3 text-zinc-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-xl transition-all"
                      >
                        <Edit size={20} />
                      </button>
                      <button 
                        onClick={() => handleDelete(patient._id)}
                        className="p-3 text-zinc-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all"
                      >
                        <Trash size={20} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xl flex items-center justify-center z-[100] p-6">
          <div className="bg-white dark:bg-gray-800 border-4 border-black dark:border-gray-700 rounded-[3rem] w-full max-w-4xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-700">
            <header className="p-12 border-b-2 border-zinc-50 dark:border-gray-700 flex justify-between items-center bg-zinc-50/50 dark:bg-gray-900/50">
               <div>
                  <h2 className="text-3xl font-black text-black dark:text-white tracking-tighter uppercase italic">
                    {editingPatient ? 'Identity Update' : 'New Enrollment'}
                  </h2>
                  <p className="text-[10px] text-blue-600 font-black uppercase tracking-[0.4em] mt-2 italic">Clinical Registry Ingestion</p>
               </div>
               <button 
                 onClick={() => setShowModal(false)}
                 className="bg-black dark:bg-gray-700 text-white p-4 rounded-xl hover:bg-blue-600 transition-all"
               >
                 <X size={24} />
               </button>
            </header>
            
            <form onSubmit={handleSubmit} className="bg-white dark:bg-gray-800">
              <div className="p-12 grid grid-cols-2 gap-10">
                <div className="space-y-4">
                  <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2">Legal Name *</label>
                  <div className="relative">
                    <UserIcon size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300" />
                    <input 
                      type="text"
                      required
                      value={formData.full_name}
                      onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                      className="w-full pl-14 pr-8 py-5 bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white rounded-2xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all font-black shadow-inner"
                      placeholder="Enter full name..."
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2">Primary Contact *</label>
                  <div className="relative">
                    <Phone size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300" />
                    <input 
                      type="tel"
                      required
                      value={formData.phone_number}
                      onChange={(e) => setFormData({...formData, phone_number: e.target.value})}
                      className="w-full pl-14 pr-8 py-5 bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white rounded-2xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all font-black shadow-inner"
                      placeholder="+1..."
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2">Gender *</label>
                  <select 
                    value={formData.gender}
                    onChange={(e) => setFormData({...formData, gender: e.target.value})}
                    className="w-full px-8 py-5 bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white rounded-2xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all font-black shadow-inner appearance-none"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div className="space-y-4">
                  <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2">Temporal Origin (DOB)</label>
                  <div className="relative">
                    <Calendar size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300" />
                    <input 
                      type="date"
                      value={formData.date_of_birth}
                      onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                      className="w-full pl-14 pr-8 py-5 bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white rounded-2xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all font-black shadow-inner"
                    />
                  </div>
                </div>

                <div className="col-span-2 space-y-4">
                  <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2">Electronic Mail</label>
                  <div className="relative">
                    <Mail size={18} className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-300" />
                    <input 
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="w-full pl-14 pr-8 py-5 bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white rounded-2xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all font-black shadow-inner"
                      placeholder="patient@network.com"
                    />
                  </div>
                </div>
              </div>
              
              <footer className="flex justify-end gap-6 p-12 bg-zinc-50/50 dark:bg-gray-900/50 border-t-2 border-zinc-50 dark:border-gray-700">
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
                  className="px-10 py-5 text-xs font-black uppercase tracking-widest text-zinc-500 hover:text-black dark:hover:text-white transition-colors"
                >
                  Abort
                </button>
                <button 
                  type="submit"
                  className="px-12 py-5 bg-blue-600 text-white text-xs font-black uppercase tracking-[0.2em] rounded-xl shadow-2xl hover:bg-blue-700 active:scale-95 transition-all flex items-center gap-3"
                >
                  {editingPatient ? 'Update Node' : 'Enroll Identity'}
                  <RefreshCw size={14} className={cn(loading && "animate-spin")} />
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
