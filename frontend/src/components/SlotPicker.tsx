import { useState, useEffect } from 'react';
import axios from 'axios';
import { Clock, Loader2, AlertCircle } from 'lucide-react';
import { cn } from '../utils/cn';

interface SlotPickerProps {
  doctorId: string;
  date: string;
  selectedTime: string;
  onSelect: (time: string) => void;
  token: string | null;
}

export default function SlotPicker({ doctorId, date, selectedTime, onSelect, token }: SlotPickerProps) {
  const [slots, setSlots] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSlots = async () => {
      if (!doctorId || !date) {
        setSlots([]);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`/api/appointments/available-slots?doctor_id=${doctorId}&target_date=${date}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setSlots(res.data.slots || []);
      } catch (err) {
        console.error('Failed to fetch slots', err);
        setError('Failed to load availability');
      } finally {
        setLoading(false);
      }
    };

    fetchSlots();
  }, [doctorId, date, token]);

  if (loading) {
    return (
      <div className="flex items-center gap-2 p-4 text-zinc-400">
        <Loader2 size={16} className="animate-spin" />
        <span className="text-[10px] font-black uppercase tracking-widest">Scanning availability...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center gap-2 p-4 text-red-500 bg-red-50 dark:bg-red-900/10 rounded-xl border border-red-100 dark:border-red-900/50">
        <AlertCircle size={16} />
        <span className="text-[10px] font-black uppercase tracking-widest">{error}</span>
      </div>
    );
  }

  if (!doctorId || !date) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-2">
        <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">Available Slots</label>
        {slots.length > 0 && (
          <span className="text-[9px] font-black text-blue-600 dark:text-blue-400 uppercase tracking-widest bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded">
            {slots.length} Slots Found
          </span>
        )}
      </div>
      
      {slots.length > 0 ? (
        <div className="grid grid-cols-3 gap-3 max-h-[200px] overflow-y-auto p-1 scrollbar-thin">
          {slots.map((slot) => {
            const time = new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            const isSelected = selectedTime === slot || selectedTime?.startsWith(slot.substring(0, 16));
            
            return (
              <button
                key={slot}
                type="button"
                onClick={() => onSelect(slot)}
                className={cn(
                  "px-4 py-3 rounded-xl border-2 text-xs font-black transition-all flex items-center justify-center gap-2",
                  isSelected
                    ? "bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-500/20"
                    : "bg-zinc-50 dark:bg-gray-900 border-transparent text-zinc-600 dark:text-gray-300 hover:border-zinc-200 dark:hover:border-gray-700"
                )}
              >
                <Clock size={12} className={isSelected ? "text-blue-200" : "text-zinc-400"} />
                {time}
              </button>
            );
          })}
        </div>
      ) : (
        <div className="p-8 text-center bg-zinc-50 dark:bg-gray-900 rounded-3xl border-2 border-dashed border-zinc-100 dark:border-gray-800">
           <AlertCircle size={24} className="mx-auto text-zinc-300 mb-2" />
           <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest">No availability on this date</p>
        </div>
      )}
    </div>
  );
}
