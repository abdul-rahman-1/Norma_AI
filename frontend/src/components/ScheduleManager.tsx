import { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, Loader2, Save, AlertCircle, CheckCircle2 } from 'lucide-react';
import { cn } from '../utils/cn';

interface ScheduleManagerProps {
  doctorId: string;
  token: string | null;
}

const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

export default function ScheduleManager({ doctorId, token }: ScheduleManagerProps) {
  const [hours, setHours] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchHours = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`/api/doctors/${doctorId}/operating-hours`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setHours(res.data);
      } catch (err) {
        console.error('Failed to fetch hours', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHours();
  }, [doctorId, token]);

  const handleUpdate = (index: number, field: string, value: any) => {
    const newHours = [...hours];
    newHours[index] = { ...newHours[index], [field]: value };
    setHours(newHours);
  };

  const saveHours = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });
    try {
      await axios.put(`/api/doctors/${doctorId}/operating-hours`, hours, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMessage({ type: 'success', text: 'Schedule saved successfully' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (err) {
      console.error('Failed to save hours', err);
      setMessage({ type: 'error', text: 'Failed to save schedule' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="py-20 flex flex-col items-center gap-4">
        <Loader2 className="animate-spin text-blue-600" size={32} />
        <p className="text-[10px] font-black uppercase tracking-widest text-zinc-400">Loading Clinical Schedule...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-h-[70vh] overflow-y-auto scrollbar-thin pb-10">
      <div className="flex justify-between items-center px-4 sticky top-0 bg-white dark:bg-gray-800 z-10 py-4 border-b dark:border-gray-700">
        <div>
           <h3 className="text-xl font-black text-black dark:text-white uppercase italic tracking-tighter">Availability Grid</h3>
           <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mt-1">Configure weekly temporal boundaries</p>
        </div>
        <button 
          onClick={saveHours}
          disabled={saving}
          className="flex items-center gap-3 bg-blue-600 text-white px-8 py-4 rounded-xl text-[10px] font-black uppercase tracking-widest shadow-xl hover:bg-blue-700 disabled:opacity-50 transition-all active:scale-95"
        >
          {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
          {saving ? 'Committing...' : 'Commit Changes'}
        </button>
      </div>

      {message.text && (
        <div className={cn(
          "mx-4 p-4 rounded-xl flex items-center gap-3 text-xs font-black uppercase tracking-widest animate-in zoom-in-95 duration-300",
          message.type === 'success' ? "bg-green-50 dark:bg-green-900/20 text-green-600 border border-green-100 dark:border-green-900/50" : "bg-red-50 dark:bg-red-900/20 text-red-600 border border-red-100 dark:border-red-900/50"
        )}>
          {message.type === 'success' ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 px-4">
        {hours.map((day, i) => (
          <div key={i} className={cn(
            "p-6 rounded-2xl border-2 transition-all flex flex-col lg:flex-row items-center justify-between gap-6",
            day.is_open ? "bg-white dark:bg-gray-800 border-zinc-50 dark:border-gray-700 shadow-sm" : "bg-zinc-50 dark:bg-gray-900 border-transparent opacity-60"
          )}>
            <div className="flex items-center gap-6 min-w-[150px]">
              <input 
                type="checkbox" 
                checked={day.is_open} 
                onChange={(e) => handleUpdate(i, 'is_open', e.target.checked)}
                className="w-6 h-6 rounded-lg border-2 border-zinc-200 dark:border-zinc-700 text-blue-600 focus:ring-blue-500 transition-all cursor-pointer"
              />
              <span className="text-sm font-black text-black dark:text-white uppercase italic tracking-tight">{DAYS[day.day_of_week]}</span>
            </div>

            <div className="flex-1 grid grid-cols-2 lg:grid-cols-4 gap-6 w-full">
              <div className="space-y-2">
                <label className="text-[9px] font-black text-zinc-400 uppercase tracking-widest ml-1">Open</label>
                <input 
                  type="time" 
                  disabled={!day.is_open}
                  value={day.open_time}
                  onChange={(e) => handleUpdate(i, 'open_time', e.target.value)}
                  className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-4 py-3 rounded-xl text-xs font-black outline-none focus:bg-white dark:focus:bg-gray-800 focus:border-blue-500 disabled:opacity-30 transition-all shadow-inner"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[9px] font-black text-zinc-400 uppercase tracking-widest ml-1">Close</label>
                <input 
                  type="time" 
                  disabled={!day.is_open}
                  value={day.close_time}
                  onChange={(e) => handleUpdate(i, 'close_time', e.target.value)}
                  className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-4 py-3 rounded-xl text-xs font-black outline-none focus:bg-white dark:focus:bg-gray-800 focus:border-blue-500 disabled:opacity-30 transition-all shadow-inner"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[9px] font-black text-zinc-400 uppercase tracking-widest ml-1">Break Start</label>
                <input 
                  type="time" 
                  disabled={!day.is_open}
                  value={day.break_start_time}
                  onChange={(e) => handleUpdate(i, 'break_start_time', e.target.value)}
                  className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-4 py-3 rounded-xl text-xs font-black outline-none focus:bg-white dark:focus:bg-gray-800 focus:border-blue-500 disabled:opacity-30 transition-all shadow-inner"
                />
              </div>
              <div className="space-y-2">
                <label className="text-[9px] font-black text-zinc-400 uppercase tracking-widest ml-1">Break End</label>
                <input 
                  type="time" 
                  disabled={!day.is_open}
                  value={day.break_end_time}
                  onChange={(e) => handleUpdate(i, 'break_end_time', e.target.value)}
                  className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white px-4 py-3 rounded-xl text-xs font-black outline-none focus:bg-white dark:focus:bg-gray-800 focus:border-blue-500 disabled:opacity-30 transition-all shadow-inner"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
