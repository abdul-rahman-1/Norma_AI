import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Calendar, Plus, MoreVertical, Edit2, Trash2, Loader2, X,
  Clock, User, Stethoscope, ChevronRight, Sparkles, Send, Zap,
  AlertCircle, CheckCircle2, Search, Filter
} from 'lucide-react';
import { cn } from '../utils/cn';

export default function Appointments() {
  const [appointments, setAppointments] = useState<any[]>([]);
  const [patients, setPatients] = useState<any[]>([]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingApt, setEditingApt] = useState<any>(null);
  
  const initialForm = {
    patient_id: '',
    doctor_id: '',
    scheduled_at: '',
    type: 'Consultation',
    notes: '',
    status: 'upcoming'
  };
  
  const [formData, setFormData] = useState(initialForm);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [aptRes, patRes, docRes] = await Promise.all([
        axios.get('http://localhost:5000/api/appointments/', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('http://localhost:5000/api/patients/', { headers: { Authorization: `Bearer ${token}` } }),
        axios.get('http://localhost:5000/api/doctors', { headers: { Authorization: `Bearer ${token}` } })
      ]);
      setAppointments(aptRes.data);
      setPatients(patRes.data);
      setDoctors(docRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('token');
    try {
      if (editingApt) {
        await axios.patch(`http://localhost:5000/api/appointments/${editingApt._id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('http://localhost:5000/api/appointments/', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      setShowModal(false);
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

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
          <h1 className="text-4xl font-black text-slate-900 tracking-tight uppercase italic">Clinical Schedule</h1>
          <p className="text-slate-500 mt-2 font-medium text-lg italic">Master orchestration of temporal clinical encounters.</p>
        </div>
        <button 
          onClick={() => { setEditingApt(null); setFormData(initialForm); setShowModal(true); }}
          className="group bg-slate-900 text-white px-10 py-5 rounded-[2rem] text-sm font-black shadow-2xl hover:bg-violet-600 transition-all flex items-center gap-4 active:scale-95"
        >
          <Calendar size={20} className="text-violet-400 group-hover:rotate-12 transition-transform" /> 
          Initialize Encounter
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        
        {/* Main List */}
        <div className="lg:col-span-8 space-y-8">
          <div className="flex items-center gap-4 bg-white/50 p-4 rounded-3xl border border-white mb-4">
             <div className="nm-inset p-3 rounded-2xl text-slate-300">
                <Search size={20} />
             </div>
             <input type="text" placeholder="Locate encounter by patient name or doctor ID..." className="bg-transparent border-none outline-none text-sm w-full font-bold text-slate-700 placeholder-slate-300" />
          </div>

          <div className="nm-luxury rounded-[3.5rem] border border-white overflow-hidden p-4">
             <div className="space-y-4">
                {appointments.length > 0 ? appointments.map((apt) => (
                  <motion.div 
                    key={apt._id}
                    whileHover={{ scale: 1.01, x: 10 }}
                    className="p-8 rounded-[2.5rem] bg-white border border-slate-100 hover:border-violet-200 hover:shadow-2xl hover:shadow-violet-500/5 transition-all group flex items-center justify-between"
                  >
                    <div className="flex items-center gap-8">
                       <div className="w-20 h-20 rounded-[1.8rem] nm-inset flex flex-col items-center justify-center text-center">
                          <p className="text-[10px] font-black text-slate-300 uppercase">{new Date(apt.scheduled_at).toLocaleDateString([], { month: 'short' })}</p>
                          <p className="text-3xl font-black text-slate-900 leading-none">{new Date(apt.scheduled_at).getDate()}</p>
                       </div>
                       <div>
                          <p className="text-xl font-black text-slate-900 tracking-tight flex items-center gap-3">
                            {apt.patient_name}
                            <span className="text-[9px] px-3 py-1 bg-slate-50 text-slate-400 rounded-lg uppercase tracking-[0.2em] font-black border border-slate-100">{apt.type}</span>
                          </p>
                          <div className="flex items-center gap-6 mt-2">
                             <p className="text-xs font-bold text-slate-400 flex items-center gap-2">
                               <Clock size={14} className="text-violet-400" />
                               {new Date(apt.scheduled_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                             </p>
                             <p className="text-xs font-bold text-slate-400 flex items-center gap-2">
                               <Stethoscope size={14} className="text-emerald-400" />
                               Dr. {doctors.find(d => d._id === apt.doctor_id)?.full_name || 'Assigned Specialist'}
                             </p>
                          </div>
                       </div>
                    </div>

                    <div className="flex items-center gap-10">
                       <div className={cn(
                         "px-6 py-2.5 rounded-2xl text-[9px] font-black uppercase tracking-widest border-2",
                         apt.status === 'upcoming' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' : 'bg-slate-50 border-slate-100 text-slate-400'
                       )}>
                         {apt.status}
                       </div>
                       <button className="nm-button-luxury w-12 h-12 rounded-2xl flex items-center justify-center text-slate-300 hover:text-violet-600">
                          <MoreVertical size={20} />
                       </button>
                    </div>
                  </motion.div>
                )) : (
                  <div className="py-32 text-center flex flex-col items-center gap-4 opacity-20 grayscale scale-90">
                     <Sparkles size={64} className="text-slate-400" />
                     <p className="text-lg font-bold text-slate-500 italic uppercase tracking-tighter">Temporal Grid Empty. No Encounters Slotted.</p>
                  </div>
                )}
             </div>
          </div>
        </div>

        {/* Sidebar Mini Node */}
        <div className="lg:col-span-4 space-y-10">
           <div className="nm-luxury p-10 rounded-[3.5rem] bg-slate-900 text-white relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-10 opacity-10 group-hover:rotate-45 transition-transform duration-1000">
                 <Zap size={150} fill="white" />
              </div>
              <h3 className="text-2xl font-black tracking-tighter uppercase italic leading-none mb-4 relative z-10">Clinical Pulse</h3>
              <p className="text-xs text-slate-400 font-bold mb-10 leading-relaxed relative z-10">"Autonomous node optimization suggests 4 priority reschedules to minimize latency."</p>
              
              <div className="space-y-6 relative z-10">
                {[
                  { label: 'Sync Status', val: 'Real-time', icon: RefreshCw },
                  { label: 'Neural Mesh', val: 'Alpha-9', icon: Zap },
                  { label: 'Integrity', val: '99.9%', icon: ShieldCheck },
                ].map((stat, i) => (
                  <div key={i} className="flex items-center justify-between p-4 rounded-2xl bg-white/5 border border-white/5">
                     <div className="flex items-center gap-3">
                        <stat.icon size={16} className="text-violet-400" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">{stat.label}</span>
                     </div>
                     <span className="text-xs font-black uppercase italic">{stat.val}</span>
                  </div>
                ))}
              </div>

              <button className="w-full mt-10 py-5 rounded-2xl bg-violet-600 text-white text-[10px] font-black uppercase tracking-[0.3em] hover:bg-white hover:text-slate-900 transition-all shadow-xl shadow-violet-600/20 active:scale-95">
                 Authorize Auto-Realign
              </button>
           </div>
        </div>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xl flex items-center justify-center z-[100] p-6">
          <div className="bg-white border border-slate-200 rounded-[3.5rem] w-full max-w-4xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-700">
            <div className="p-12 border-b border-slate-50 flex justify-between items-center bg-slate-50/50">
               <div>
                  <h2 className="text-3xl font-black text-slate-900 tracking-tighter uppercase italic">Encounter Setup</h2>
                  <p className="text-[10px] text-slate-400 font-black uppercase tracking-[0.4em] mt-2 italic">Neural Temporal Alignment Node</p>
               </div>
               <button onClick={() => setShowModal(false)} className="bg-white p-4 rounded-2xl text-slate-300 hover:text-red-500 border border-slate-100 transition-all shadow-sm">
                 <X size={28} />
               </button>
            </div>

            <form onSubmit={handleSubmit} className="p-12 grid grid-cols-2 gap-10">
              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Patient Asset *</label>
                <select required className="w-full bg-slate-50 border-2 border-transparent text-slate-900 px-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner appearance-none" value={formData.patient_id} onChange={e => setFormData({...formData, patient_id: e.target.value})}>
                  <option value="">Select Identity...</option>
                  {patients.map(p => <option key={p._id} value={p._id}>{p.full_name}</option>)}
                </select>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Assigned Specialist *</label>
                <select required className="w-full bg-slate-50 border-2 border-transparent text-slate-900 px-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner appearance-none" value={formData.doctor_id} onChange={e => setFormData({...formData, doctor_id: e.target.value})}>
                  <option value="">Select Provider...</option>
                  {doctors.map(d => <option key={d._id} value={d._id}>{d.full_name}</option>)}
                </select>
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Temporal Slot *</label>
                <input type="datetime-local" required className="w-full bg-slate-50 border-2 border-transparent text-slate-900 px-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner" value={formData.scheduled_at} onChange={e => setFormData({...formData, scheduled_at: e.target.value})} />
              </div>

              <div className="space-y-4">
                <label className="text-[10px] font-black text-slate-400 uppercase tracking-[0.25em] ml-2">Encounter Protocol</label>
                <select className="w-full bg-slate-50 border-2 border-transparent text-slate-900 px-8 py-6 rounded-[1.8rem] outline-none focus:bg-white focus:border-violet-200 transition-all text-base font-black shadow-inner appearance-none" value={formData.type} onChange={e => setFormData({...formData, type: e.target.value})}>
                  <option value="Consultation">Standard Consult</option>
                  <option value="Surgery">Surgical Procedure</option>
                  <option value="Follow-up">Neural Follow-up</option>
                  <option value="Emergency">Urgent Response</option>
                </select>
              </div>

              <div className="col-span-2 pt-10 flex gap-8">
                <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-white text-slate-400 py-6 rounded-[2rem] font-black uppercase tracking-[0.3em] text-xs border-2 border-slate-100 transition-all shadow-sm">Cancel Sequence</button>
                <button type="submit" className="flex-1 bg-slate-900 text-white py-6 rounded-[2rem] font-black uppercase tracking-[0.3em] text-xs shadow-2xl hover:bg-violet-600 transition-all active:scale-95 flex items-center justify-center gap-4">
                   {editingApt ? 'Confirm Realignment' : 'Authorize Encounter'}
                   <Zap size={18} className="text-violet-400" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
