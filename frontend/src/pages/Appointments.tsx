import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  Calendar, Plus, Edit2, Trash2, Loader2, X,
  Clock, Stethoscope, Sparkles, Zap
} from 'lucide-react';
import { cn } from '../utils/cn';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import SlotPicker from '../components/SlotPicker';
import PatientSearch from '../components/PatientSearch';

export default function Appointments() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingApt, setEditingApt] = useState<any>(null);
  const { token } = useAuth();
  
  const initialForm = {
    patient_id: '',
    doctor_id: '',
    appointment_datetime: '',
    appointment_type: 'consultation',
    notes: '',
    status: 'booked'
  };
  
  const [formData, setFormData] = useState(initialForm);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [aptRes, docRes] = await Promise.all([
        axios.get('/api/appointments', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('/api/doctors', { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setAppointments(aptRes.data);
      setDoctors(docRes.data);
    } catch (err) {
      console.error('Failed to synchronize data', err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    if (!formData.appointment_datetime) {
        alert("Please select an available time slot.");
        return;
    }

    try {
      if (editingApt) {
        await axios.patch(`/api/appointments/${editingApt._id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('/api/appointments', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setShowModal(false);
      fetchData();
    } catch (err) {
      console.error('Operation failed', err);
      alert('Failed to save appointment. Please ensure the slot is still available.');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Cancel this appointment?')) return;
    try {
      await axios.delete(`/api/appointments/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchData();
    } catch (err) {
      console.error('Delete failed', err);
    }
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-white dark:bg-gray-900">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="animate-spin text-blue-600" size={40} />
          <p className="text-xs font-black uppercase tracking-[0.3em] text-zinc-400">Syncing Clinical Grid...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1400px] mx-auto space-y-12 animate-in fade-in duration-700 pb-20">
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6">
        <div>
          <h1 className="text-4xl font-black text-black dark:text-white tracking-tight uppercase italic">Appointments</h1>
          <p className="text-zinc-500 mt-2 font-bold text-lg">Manage clinical encounters and provider schedules.</p>
        </div>
        <button 
          onClick={() => { 
            setEditingApt(null); 
            setFormData(initialForm); 
            setSelectedDate(new Date().toISOString().split('T')[0]);
            setShowModal(true); 
          }}
          className="group bg-blue-600 text-white px-10 py-5 rounded-xl text-xs font-black uppercase tracking-[0.2em] shadow-2xl hover:bg-blue-700 transition-all flex items-center gap-4 active:scale-95"
        >
          <Calendar size={18} className="text-white group-hover:rotate-12 transition-transform" /> 
          Book Appointment
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        <div className="lg:col-span-8 space-y-8">
          <div className="bg-white dark:bg-gray-800 rounded-[2rem] border-2 border-zinc-50 dark:border-gray-700 overflow-hidden shadow-sm p-4">
             <div className="space-y-4">
                {appointments.length > 0 ? appointments.map((apt) => (
                  <motion.div 
                    key={apt._id}
                    whileHover={{ scale: 1.01, x: 10 }}
                    className="p-8 rounded-2xl bg-zinc-50/50 dark:bg-gray-900/50 border border-zinc-100 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 hover:bg-white dark:hover:bg-gray-800 transition-all group flex items-center justify-between"
                  >
                    <div className="flex items-center gap-8">
                       <div className="w-16 h-16 rounded-xl bg-blue-600 flex flex-col items-center justify-center text-center">
                          <p className="text-[9px] font-black text-blue-200 uppercase">{new Date(apt.appointment_datetime).toLocaleDateString([], { month: 'short' })}</p>
                          <p className="text-2xl font-black text-white leading-none">{new Date(apt.appointment_datetime).getDate()}</p>
                       </div>
                       <div>
                          <p className="text-xl font-black text-black dark:text-white tracking-tight flex items-center gap-3">
                            {apt.patient?.name || 'Unknown Patient'}
                            <span className="text-[9px] px-3 py-1 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded font-black uppercase tracking-widest">{apt.appointment_type}</span>
                          </p>
                          <div className="flex items-center gap-6 mt-2">
                             <p className="text-xs font-bold text-zinc-400 flex items-center gap-2">
                               <Clock size={14} className="text-blue-500" />
                               {new Date(apt.appointment_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                             </p>
                             <p className="text-xs font-bold text-zinc-400 flex items-center gap-2">
                               <Stethoscope size={14} className="text-blue-500" />
                               {apt.doctor?.name ? `Dr. ${apt.doctor.name}` : 'No Provider Assigned'}
                             </p>
                          </div>
                       </div>
                    </div>

                    <div className="flex items-center gap-10">
                       <div className={cn(
                         "px-5 py-2 rounded-lg text-[9px] font-black uppercase tracking-widest border-2",
                         apt.status === 'booked' ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 border-blue-200 dark:border-blue-800' : 'bg-white dark:bg-gray-800 text-zinc-300 border-zinc-100 dark:border-gray-700'
                       )}>
                         {apt.status}
                       </div>
                       <div className="flex gap-2">
                        <button 
                          onClick={() => { 
                            setEditingApt(apt); 
                            setFormData({...apt, appointment_datetime: apt.appointment_datetime}); 
                            setSelectedDate(apt.appointment_datetime.split('T')[0]);
                            setShowModal(true); 
                          }}
                          className="text-zinc-300 hover:text-blue-600 p-2 rounded-lg transition-colors"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button 
                          onClick={() => handleDelete(apt._id)}
                          className="text-zinc-300 hover:text-red-600 p-2 rounded-lg transition-colors"
                        >
                          <Trash2 size={18} />
                        </button>
                       </div>
                    </div>
                  </motion.div>
                )) : (
                  <div className="py-32 text-center flex flex-col items-center gap-4 opacity-20 grayscale scale-90">
                     <Sparkles size={64} className="text-black dark:text-white" />
                     <p className="text-lg font-bold text-black dark:text-white italic uppercase tracking-tighter">No appointments found.</p>
                  </div>
                )}
             </div>
          </div>
        </div>

        <div className="lg:col-span-4 space-y-10">
           <div className="bg-blue-600 dark:bg-blue-700 text-white p-10 rounded-[2.5rem] relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-10 opacity-10 group-hover:rotate-45 transition-transform duration-1000">
                 <Zap size={150} fill="white" />
              </div>
              <h3 className="text-2xl font-black tracking-tighter uppercase italic mb-4 relative z-10">Clinic Activity</h3>
              <p className="text-blue-100 text-xs font-bold mb-10 leading-relaxed relative z-10">System is managing {appointments.length} active clinical nodes.</p>
              
              <div className="space-y-4 relative z-10">
                {[
                  { label: 'Upcoming', val: appointments.filter(a => a.status === 'booked').length, icon: Calendar },
                  { label: 'Completed', val: appointments.filter(a => a.status === 'completed').length, icon: Sparkles },
                ].map((stat, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-white/10 rounded-xl border border-white/5">
                     <span className="text-[10px] font-black uppercase tracking-widest text-blue-100">{stat.label}</span>
                     <span className="text-xl font-black italic">{stat.val}</span>
                  </div>
                ))}
              </div>
           </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-xl flex items-center justify-center z-[100] p-6">
          <div className="bg-white dark:bg-gray-800 border-4 border-black dark:border-gray-700 rounded-[3rem] w-full max-w-4xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-700">
            <div className="p-12 border-b-2 border-zinc-50 dark:border-gray-700 flex justify-between items-center bg-zinc-50/50 dark:bg-gray-900/50">
               <div>
                  <h2 className="text-3xl font-black text-black dark:text-white tracking-tighter uppercase italic">{editingApt ? 'Reschedule' : 'Temporal Slotting'}</h2>
                  <p className="text-[10px] text-blue-600 font-black uppercase tracking-[0.4em] mt-2 italic">Clinical Encounter Alignment</p>
               </div>
               <button onClick={() => setShowModal(false)} className="bg-black dark:bg-gray-700 text-white p-4 rounded-xl hover:bg-blue-600 transition-all">
                 <X size={24} />
               </button>
            </div>

            <form onSubmit={handleSubmit} className="p-12 bg-white dark:bg-gray-800">
              <div className="grid grid-cols-2 gap-10">
                <div className="space-y-8">
                  <PatientSearch 
                    selectedPatientId={formData.patient_id}
                    onSelect={(id) => setFormData({...formData, patient_id: id})}
                    token={token}
                  />

                  <div className="space-y-4">
                    <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2 block">Provider *</label>
                    <select required className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-8 py-5 rounded-xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all text-sm font-black shadow-inner appearance-none" value={formData.doctor_id} onChange={e => setFormData({...formData, doctor_id: e.target.value})}>
                      <option value="">Select provider...</option>
                      {doctors.map(d => <option key={d._id} value={d._id}>{d.full_name}</option>)}
                    </select>
                  </div>

                  <div className="space-y-4">
                    <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2 block">Target Date *</label>
                    <input type="date" required className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-8 py-5 rounded-xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all text-sm font-black shadow-inner" value={selectedDate} onChange={e => { setSelectedDate(e.target.value); setFormData({...formData, appointment_datetime: ''}); }} />
                  </div>
                </div>

                <div className="space-y-8">
                  <SlotPicker 
                    doctorId={formData.doctor_id}
                    date={selectedDate}
                    selectedTime={formData.appointment_datetime}
                    onSelect={(time) => setFormData({...formData, appointment_datetime: time})}
                    token={token}
                  />
                  
                  <div className="space-y-4">
                    <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2 block">Encounter Type</label>
                    <select className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-8 py-5 rounded-xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all text-sm font-black shadow-inner appearance-none" value={formData.appointment_type} onChange={e => setFormData({...formData, appointment_type: e.target.value})}>
                      <option value="consultation">Consultation</option>
                      <option value="follow_up">Follow Up</option>
                      <option value="procedure">Procedure</option>
                      <option value="emergency">Emergency</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="pt-12 flex gap-8">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-zinc-100 dark:bg-gray-700 text-black dark:text-white py-6 rounded-xl font-black uppercase tracking-widest text-xs hover:bg-zinc-200 dark:hover:bg-gray-600 transition-all">Abort</button>
                <button type="submit" className="flex-1 bg-blue-600 text-white py-6 rounded-xl font-black uppercase tracking-widest text-xs hover:bg-blue-700 transition-all shadow-2xl active:scale-95 flex items-center justify-center gap-4">
                   {editingApt ? 'Update Sequence' : 'Commit Slot'}
                   <Zap size={16} className="text-blue-200" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
