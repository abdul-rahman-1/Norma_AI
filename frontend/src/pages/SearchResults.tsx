import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, User, Stethoscope, Briefcase, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

export default function SearchResults() {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';
  const [results, setResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { token } = useAuth();
  const navigate = useNavigate();

  const fetchResults = useCallback(async () => {
    if (!query || query.length < 2 || !token) {
      setIsLoading(false);
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const res = await axios.get(`/api/dashboard/search`, {
        params: { q: query },
        headers: { Authorization: `Bearer ${token}` }
      });
      setResults(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch search results');
    } finally {
      setIsLoading(false);
    }
  }, [query, token]);

  useEffect(() => {
    fetchResults();
  }, [fetchResults]);

  const getIcon = (type: string) => {
    switch (type) {
      case 'Patient': return <User size={24} className="text-blue-500" />;
      case 'Doctor': return <Stethoscope size={24} className="text-green-500" />;
      case 'Staff': return <Briefcase size={24} className="text-purple-500" />;
      default: return <User size={24} className="text-gray-500" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <Loader2 size={40} className="animate-spin text-blue-600 mb-4" />
        <p className="text-gray-500 dark:text-gray-400 font-bold uppercase tracking-widest text-xs">Searching global records...</p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-20">
      <header>
        <div className="flex items-center gap-4 mb-2">
          <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-2xl text-blue-600 dark:text-blue-400">
            <Search size={28} />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Search Results</h1>
            <p className="text-gray-500 dark:text-gray-400">Showing results for <span className="text-blue-600 dark:text-blue-400 font-bold">"{query}"</span> across clinical collections.</p>
          </div>
        </div>
      </header>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-xl flex items-center gap-3 font-medium">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {results.length === 0 && !error ? (
        <div className="flex flex-col items-center justify-center p-20 bg-white dark:bg-gray-800 rounded-[2.5rem] border border-gray-200 dark:border-gray-700 shadow-sm text-center">
          <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-[2rem] flex items-center justify-center mb-6">
            <Search size={36} className="text-gray-400" />
          </div>
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 uppercase tracking-tight italic">No Information Found</h3>
          <p className="text-gray-500 dark:text-gray-400 max-w-md font-medium">
            We couldn't find any patients, doctors, or staff matching your query. Ensure spelling is correct or try a different phone number.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {results.map((result, idx) => (
            <div 
              key={idx} 
              onClick={() => navigate(result.link)}
              className="bg-white dark:bg-gray-800 p-6 rounded-[2rem] border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-xl hover:border-blue-500/50 transition-all cursor-pointer flex flex-col gap-6 group"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-2xl bg-gray-50 dark:bg-gray-900 flex items-center justify-center group-hover:bg-blue-50 dark:group-hover:bg-blue-900/30 transition-colors">
                    {getIcon(result.type)}
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{result.title}</h3>
                    <p className="text-[10px] font-black text-gray-400 dark:text-gray-500 uppercase tracking-widest">{result.type}</p>
                  </div>
                </div>
                <span className="text-[10px] uppercase font-black tracking-tighter italic px-3 py-1 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                  {result.status}
                </span>
              </div>
              
              <div className="pt-6 border-t dark:border-gray-700 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="font-bold text-gray-400 dark:text-gray-500 uppercase text-[10px] tracking-widest">Details</span>
                  <span className="font-bold text-gray-800 dark:text-gray-200">{result.subtitle || 'N/A'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="font-bold text-gray-400 dark:text-gray-500 uppercase text-[10px] tracking-widest">Contact</span>
                  <span className="font-bold text-gray-800 dark:text-gray-200">{result.contact || 'N/A'}</span>
                </div>
              </div>
              
              <button className="mt-2 w-full py-3 bg-gray-50 dark:bg-gray-900 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 group-hover:bg-blue-600 group-hover:text-white transition-all">
                Access Profile
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
