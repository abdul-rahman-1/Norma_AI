import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ShieldCheck, Loader2 } from 'lucide-react';
import axios from 'axios';

const AdminLogin = () => {
  const [username, setUsername] = useState('norma_admin');
  const [password, setPassword] = useState('norma2026');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await axios.post('/api/auth/admin-login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const data = response.data;
      login(data.access_token, data.role, data.name);
      navigate('/admin-dashboard');

    } catch (err: any) {
      console.error("Admin login failed", err);
      setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const inputStyles = "w-full px-4 py-2.5 mt-1 text-sm bg-gray-100 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900";
  const buttonStyles = "w-full py-3 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-60 flex items-center justify-center gap-2";

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="w-full max-w-sm p-8 space-y-6 bg-white rounded-2xl shadow-sm border border-gray-200">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600 text-white mb-4">
            <ShieldCheck size={24} />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Administrator Portal</h1>
          <p className="text-sm text-gray-500 mt-2">Root access for system configuration</p>
        </div>

        {error && <p className="text-red-500 text-xs text-center font-semibold bg-red-50 p-3 rounded-lg">{error}</p>}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-xs font-semibold text-gray-600">Admin Username</label>
            <input
              id="username"
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={inputStyles}
              placeholder="Enter your admin username"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-xs font-semibold text-gray-600">Password</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputStyles}
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className={buttonStyles}
          >
            {isLoading ? <Loader2 className="animate-spin" size={20} /> : 'Authorize Access'}
          </button>
        </form>

        <div className="text-center pt-4 border-t border-gray-100">
          <a href="/login" className="text-xs font-semibold text-gray-500 hover:text-blue-600">
            Switch to Doctor & Staff Login
          </a>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
