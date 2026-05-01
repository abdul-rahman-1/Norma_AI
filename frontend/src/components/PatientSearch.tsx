import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Search, User, Loader2, X, Plus } from 'lucide-react';
import { cn } from '../utils/cn';

interface PatientSearchProps {
  selectedPatientId: string;
  onSelect: (patientId: string, patientName: string) => void;
  token: string | null;
}

export default function PatientSearch({ selectedPatientId, onSelect, token }: PatientSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedName, setSelectedName] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchPatients = async () => {
      if (query.length < 2) {
        setResults([]);
        return;
      }

      setLoading(true);
      try {
        const res = await axios.get('/api/patients', {
          headers: { Authorization: `Bearer ${token}` }
        });
        // Filter in frontend for now as API doesn't support search yet
        const filtered = res.data.filter((p: any) => 
          p.full_name.toLowerCase().includes(query.toLowerCase()) || 
          p.phone_number.includes(query)
        );
        setResults(filtered);
      } catch (err) {
        console.error('Patient search failed', err);
      } finally {
        setLoading(false);
      }
    };

    const timer = setTimeout(fetchPatients, 300);
    return () => clearTimeout(timer);
  }, [query, token]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch initial patient name if ID is provided
  useEffect(() => {
    if (selectedPatientId && !selectedName) {
        const fetchPatient = async () => {
            try {
                const res = await axios.get(`/api/patients/${selectedPatientId}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                setSelectedName(res.data.full_name);
            } catch (err) {
                console.error("Failed to fetch selected patient", err);
            }
        };
        fetchPatient();
    }
  }, [selectedPatientId, token, selectedName]);

  return (
    <div className="relative" ref={containerRef}>
      <label className="text-[10px] font-black text-zinc-400 uppercase tracking-widest ml-2 block mb-3">Identity *</label>
      
      {selectedPatientId && !showResults ? (
        <div className="flex items-center justify-between w-full bg-zinc-900 text-white px-8 py-5 rounded-xl border-2 border-zinc-900 shadow-xl group">
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-[10px] font-black">
              {selectedName ? selectedName[0] : 'P'}
            </div>
            <div>
                <p className="text-sm font-black">{selectedName || 'Loading...'}</p>
                <p className="text-[9px] font-black text-zinc-500 uppercase tracking-widest mt-1">Patient Selected</p>
            </div>
          </div>
          <button 
            type="button"
            onClick={() => { onSelect('', ''); setSelectedName(''); setShowResults(true); setQuery(''); }}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X size={16} />
          </button>
        </div>
      ) : (
        <div className="relative group">
          <div className="absolute left-6 top-1/2 -translate-y-1/2 text-zinc-400 group-focus-within:text-blue-500 transition-colors">
            {loading ? <Loader2 size={18} className="animate-spin" /> : <Search size={18} />}
          </div>
          <input 
            type="text"
            placeholder="Search name or phone..."
            className="w-full bg-zinc-50 dark:bg-gray-900 border-2 border-transparent text-black dark:text-white pl-16 pr-8 py-5 rounded-xl outline-none focus:bg-white dark:focus:bg-gray-900 focus:border-blue-500 transition-all text-sm font-black shadow-inner"
            value={query}
            onChange={(e) => { setQuery(e.target.value); setShowResults(true); }}
            onFocus={() => setShowResults(true)}
          />
        </div>
      )}

      {showResults && query.length >= 2 && (
        <div className="absolute top-full left-0 w-full mt-3 bg-white dark:bg-gray-800 border-2 border-zinc-100 dark:border-gray-700 rounded-[2rem] shadow-2xl z-50 overflow-hidden max-h-[300px] overflow-y-auto scrollbar-thin animate-in slide-in-from-top-2 duration-300">
          {results.length > 0 ? (
            <div className="p-3 space-y-2">
              {results.map((patient) => (
                <button
                  key={patient._id}
                  type="button"
                  onClick={() => {
                    onSelect(patient._id, patient.full_name);
                    setSelectedName(patient.full_name);
                    setShowResults(false);
                    setQuery('');
                  }}
                  className="w-full flex items-center justify-between p-4 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-2xl transition-all group border border-transparent hover:border-blue-100 dark:hover:border-blue-900/50"
                >
                  <div className="flex items-center gap-4 text-left">
                    <div className="w-10 h-10 rounded-xl bg-zinc-100 dark:bg-gray-700 flex items-center justify-center text-zinc-500 group-hover:bg-blue-600 group-hover:text-white transition-all">
                      <User size={18} />
                    </div>
                    <div>
                      <p className="text-sm font-black text-slate-800 dark:text-white">{patient.full_name}</p>
                      <p className="text-[10px] font-black text-zinc-400 uppercase tracking-widest mt-1">{patient.phone_number}</p>
                    </div>
                  </div>
                  <Plus size={16} className="text-zinc-300 group-hover:text-blue-600" />
                </button>
              ))}
            </div>
          ) : (
            <div className="p-10 text-center opacity-40">
              <Search size={32} className="mx-auto mb-4" />
              <p className="text-[10px] font-black uppercase tracking-widest">No matches found</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
