import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Activity, Loader2 } from 'lucide-react';
import axios from 'axios';

const Login = () => {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await axios.post('/api/auth/request-otp', { phone_number: phone });
      setStep(2);
    } catch (err: any) {
      console.error("OTP request failed", err);
      setError(err.response?.data?.detail || 'Failed to send OTP. Is the phone number registered?');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.post('/api/auth/login', { 
        name, 
        phone_number: phone, 
        otp 
      });

      const data = response.data;
      login(data.access_token, data.role, data.name);
      navigate(data.role === 'admin' ? '/admin-dashboard' : '/dashboard');

    } catch (err: any) {
      console.error("Login failed", err);
      setError(err.response?.data?.detail || 'Login failed. Please check your OTP and try again.');
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
            <Activity size={24} />
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Doctor & Staff Portal</h1>
          <p className="text-sm text-gray-500 mt-2">Welcome to Norma AI</p>
        </div>

        {error && <p className="text-red-500 text-xs text-center font-semibold bg-red-50 p-3 rounded-lg">{error}</p>}

        {step === 1 ? (
          <form onSubmit={handleRequestOtp} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-xs font-semibold text-gray-600">Full Name</label>
              <input
                id="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className={inputStyles}
                placeholder="Your registered full name"
              />
            </div>
            <div>
              <label htmlFor="phone" className="block text-xs font-semibold text-gray-600">Phone Number</label>
              <input
                id="phone"
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className={inputStyles}
                placeholder="e.g., +15551234567"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || !name || !phone}
              className={buttonStyles}
            >
              {isLoading ? <Loader2 className="animate-spin" size={20} /> : 'Continue'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleLogin} className="space-y-4">
            <p className="text-sm text-center text-gray-600">
              We've sent a one-time password to <br />
              <span className="font-semibold">{phone}</span>.
            </p>
            <div>
              <label htmlFor="otp" className="block text-xs font-semibold text-gray-600">Verification Code</label>
              <input
                id="otp"
                type="text"
                required
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                className={inputStyles + ' text-center tracking-widest'}
                placeholder="••••••"
              />
            </div>
            <button
              type="submit"
              disabled={isLoading || otp.length < 6}
              className={buttonStyles}
            >
              {isLoading ? <Loader2 className="animate-spin" size={20} /> : 'Login Securely'}
            </button>
            <button
              type="button"
              onClick={() => { setStep(1); setError(''); }}
              className="w-full text-xs text-center font-semibold text-gray-500 hover:text-blue-600"
            >
              Use a different phone number
            </button>
          </form>
        )}
         <div className="text-center pt-4 border-t border-gray-100">
            <a href="/admin-login" className="text-xs font-semibold text-gray-500 hover:text-blue-600">
              Switch to Administrator Login
            </a>
          </div>
      </div>
    </div>
  );
};

export default Login;
