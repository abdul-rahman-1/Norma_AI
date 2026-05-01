import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Loader2, Plus, Search, Edit, Trash, X, AlertCircle, Stethoscope, Mail, Phone, Award, DollarSign, CalendarDays } from 'lucide-react';
import axios from 'axios';
import ScheduleManager from '../components/ScheduleManager';

export default function Doctors() {
  const [doctors, setDoctors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState<any>(null);
  const [activeDoctorId, setActiveDoctorId] = useState<string | null>(null);
  const { token } = useAuth();
  
  const initialForm = {
    full_name: '',
    specialty: '',
    license_number: '',
    whatsapp_number: '',
    email: '',
    consultation_fee: 0,
    is_active: true
  };
  
  const [formData, setFormData] = useState(initialForm);

  const fetchDoctors = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError('');
    try {
      const res = await axios.get('/api/doctors', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDoctors(res.data);
    } catch (err: any) { 
      setError(err.response?.data?.detail || err.message || "Failed to fetch doctors");
    } finally { 
      setLoading(false); 
    }
  }, [token]);

  useEffect(() => {
    fetchDoctors();
  }, [fetchDoctors]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const url = editingDoctor ? `/api/doctors/${editingDoctor._id}` : '/api/doctors';
    const method = editingDoctor ? 'patch' : 'post';

    try {
      await axios({
        method,
        url,
        data: formData,
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowModal(false);
      fetchDoctors();
    } catch (err: any) { 
      setError(err.response?.data?.detail || err.message || 'Operation failed.');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to archive this doctor?')) return;
    try {
      await axios.delete(`/api/doctors/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDoctors();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Archive failed.');
    }
  };

  const openEditModal = (doctor: any) => {
    setEditingDoctor(doctor);
    setFormData({ ...doctor });
    setShowModal(true);
  };

  const openScheduleModal = (id: string) => {
    setActiveDoctorId(id);
    setShowScheduleModal(true);
  };

  const filteredDoctors = doctors.filter(d => 
    d.full_name?.toLowerCase().includes(search.toLowerCase()) || 
    d.specialty?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white">Medical Providers</h1>
          <p className="text-md text-gray-500 dark:text-gray-400 mt-1">Manage specialist profiles and system access.</p>
        </div>
        <button 
          onClick={() => { setEditingDoctor(null); setFormData(initialForm); setShowModal(true); }}
          className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <Plus size={18} />
          Register Doctor
        </button>
      </header>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-xl flex items-center gap-3 font-medium text-sm">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      <div className="relative">
        <Search size={18} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
        <input 
          type="text" 
          placeholder="Search by name or specialty..." 
          className="w-full h-11 pl-10 pr-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full py-20 flex justify-center">
            <Loader2 className="animate-spin text-blue-600" size={40} />
          </div>
        ) : filteredDoctors.length === 0 ? (
          <div className="col-span-full py-20 text-center bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 text-gray-500">
            No providers found matching your search.
          </div>
        ) : filteredDoctors.map((doctor) => (
          <div key={doctor._id} className="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow flex flex-col h-full">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400">
                  <Stethoscope size={24} />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 dark:text-white">{doctor.full_name}</h3>
                  <p className="text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider">{doctor.specialty}</p>
                </div>
              </div>
              <span className={`px-2 py-1 text-[10px] font-bold uppercase tracking-wider rounded-full ${doctor.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'}`}>
                {doctor.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div className="space-y-3 pt-4 border-t dark:border-gray-700">
              <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                <Mail size={16} />
                <span className="truncate">{doctor.email || 'No email provided'}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                <Phone size={16} />
                <span>{doctor.whatsapp_number}</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-400">
                <Award size={16} />
                <span>License: {doctor.license_number}</span>
              </div>
            </div>

            <div className="flex-1 min-h-[20px]"></div>

            <div className="flex flex-col gap-4 mt-6 pt-4 border-t dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1 text-gray-900 dark:text-white font-bold">
                  <DollarSign size={16} />
                  <span>{doctor.consultation_fee}</span>
                </div>
                <div className="flex gap-2">
                    <button 
                    onClick={() => openEditModal(doctor)}
                    className="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                    >
                    <Edit size={18} />
                    </button>
                    <button 
                    onClick={() => handleDelete(doctor._id)}
                    className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                    >
                    <Trash size={18} />
                    </button>
                </div>
              </div>
              
              <button 
                onClick={() => openScheduleModal(doctor._id)}
                className="w-full flex items-center justify-center gap-2 py-3 bg-zinc-900 dark:bg-gray-700 text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-blue-600 dark:hover:bg-blue-600 transition-all active:scale-95 shadow-xl"
              >
                <CalendarDays size={14} />
                Manage Schedule
              </button>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
            <header className="flex justify-between items-center p-6 border-b dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-800 dark:text-white">
                {editingDoctor ? 'Edit Doctor Profile' : 'Register New Specialist'}
              </h2>
              <button 
                onClick={() => setShowModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
              >
                <X size={20} className="text-gray-500" />
              </button>
            </header>
            
            <form onSubmit={handleSubmit}>
              <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto scrollbar-thin">
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Full Name</label>
                  <input 
                    type="text"
                    required
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                    placeholder="Dr. Full Name"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Specialty</label>
                    <input 
                      type="text"
                      required
                      value={formData.specialty}
                      onChange={(e) => setFormData({...formData, specialty: e.target.value})}
                      className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                      placeholder="e.g. Cardiology"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">License Number</label>
                    <input 
                      type="text"
                      required
                      value={formData.license_number}
                      onChange={(e) => setFormData({...formData, license_number: e.target.value})}
                      className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                      placeholder="LIC-12345"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">WhatsApp Number</label>
                    <input 
                      type="tel"
                      required
                      value={formData.whatsapp_number}
                      onChange={(e) => setFormData({...formData, whatsapp_number: e.target.value})}
                      className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                      placeholder="+1..."
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Consultation Fee</label>
                    <input 
                      type="number"
                      required
                      value={formData.consultation_fee}
                      onChange={(e) => setFormData({...formData, consultation_fee: Number(e.target.value)})}
                      className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                    />
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Email Address</label>
                  <input 
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="w-full px-4 py-2.5 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-white"
                    placeholder="doctor@example.com"
                  />
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <input 
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label htmlFor="is_active" className="text-sm font-semibold text-gray-700 dark:text-gray-300">Active and available for consultations</label>
                </div>
              </div>
              
              <footer className="flex justify-end gap-3 p-6 bg-gray-50 dark:bg-gray-800/50 border-t dark:border-gray-700">
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
                  className="px-6 py-2.5 text-sm font-bold text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-xl transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="px-8 py-2.5 bg-blue-600 text-white text-sm font-bold rounded-xl shadow-lg shadow-blue-500/25 hover:bg-blue-700 active:scale-95 transition-all"
                >
                  {editingDoctor ? 'Update Profile' : 'Register Doctor'}
                </button>
              </footer>
            </form>
          </div>
        </div>
      )}

      {showScheduleModal && activeDoctorId && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-xl flex items-center justify-center z-[110] p-6">
           <div className="bg-white dark:bg-gray-800 border-4 border-black dark:border-gray-700 rounded-[3rem] w-full max-w-5xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-500">
              <div className="p-8 border-b-2 border-zinc-50 dark:border-gray-700 flex justify-between items-center bg-zinc-50/50 dark:bg-gray-900/50">
                 <div>
                    <h2 className="text-2xl font-black text-black dark:text-white uppercase italic tracking-tighter">Clinical Grid Alignment</h2>
                    <p className="text-[10px] text-blue-600 font-black uppercase tracking-[0.4em] mt-1">Temporal Provider Configuration</p>
                 </div>
                 <button onClick={() => setShowScheduleModal(false)} className="bg-black dark:bg-gray-700 text-white p-4 rounded-xl hover:bg-red-600 transition-all shadow-xl">
                   <X size={20} />
                 </button>
              </div>
              <div className="p-4 bg-white dark:bg-gray-800">
                <ScheduleManager doctorId={activeDoctorId} token={token} />
              </div>
           </div>
        </div>
      )}
    </div>
  );
}
