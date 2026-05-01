import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, Shield, Activity, CheckCircle2, 
  Loader2, Lock, Smartphone, Sliders, Database, AlertCircle
} from 'lucide-react';
import { cn } from '../utils/cn';
import { useAuth } from '../contexts/AuthContext';

export default function Settings() {
  const { userName, userRole, token, login } = useAuth();
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState("Identity Profile");

  // Form states
  const [name, setName] = useState(userName || '');
  const [password, setPassword] = useState('');

  useEffect(() => {
    setName(userName || '');
  }, [userName]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    
    try {
      const payload: any = {};
      if (name && name !== userName) payload.name = name;
      if (password) payload.password = password;

      if (Object.keys(payload).length > 0) {
        const res = await fetch('/api/auth/profile', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Failed to update profile');
        }

        const data = await res.json();
        if (data.name && token && userRole) {
          // Re-login to update context and local storage immediately
          login(token, userRole, data.name);
        }
      }

      setToast(true);
      setPassword(''); // Clear password field
      setTimeout(() => setToast(false), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const sections = [
    { title: "Identity Profile", icon: User },
    { title: "System & Security", icon: Shield },
    { title: "System Engine", icon: Activity }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }} 
      animate={{ opacity: 1, y: 0 }} 
      className="max-w-5xl mx-auto space-y-8 pb-32"
    >
      <header className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Configuration</h1>
        <p className="text-gray-500 dark:text-gray-400">Manage your system preferences and security settings.</p>
      </header>

      <AnimatePresence>
        {toast && (
          <motion.div 
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-10 left-1/2 -translate-x-1/2 z-50 bg-green-600 text-white px-6 py-3 rounded-lg flex items-center gap-3 shadow-xl text-sm font-semibold"
          >
            <CheckCircle2 size={18} />
            Configuration Saved Successfully
          </motion.div>
        )}
      </AnimatePresence>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-xl flex items-center gap-3 font-medium text-sm">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        
        {/* Left Side: Navigation Links */}
        <div className="md:col-span-4 space-y-3">
          {sections.map((section) => (
            <button 
              key={section.title}
              onClick={() => setActiveTab(section.title)}
              className={cn(
                "w-full flex items-center gap-3 p-4 rounded-xl transition-all duration-200 text-left font-semibold text-sm",
                activeTab === section.title 
                  ? "bg-blue-600 text-white shadow-md" 
                  : "bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 border border-gray-200 dark:border-gray-700"
              )}
            >
              <section.icon size={18} />
              {section.title}
            </button>
          ))}
        </div>

        {/* Right Side: Active Settings Panel */}
        <div className="md:col-span-8">
          <form onSubmit={handleSave} className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
            
            <div className="mb-8 pb-6 border-b border-gray-100 dark:border-gray-700">
               <h2 className="text-xl font-bold text-gray-900 dark:text-white">{activeTab}</h2>
               <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                 {activeTab === "Identity Profile" && "Manage your personal details and role."}
                 {activeTab === "System & Security" && "Update your password and authentication methods."}
                 {activeTab === "System Engine" && "Configure AI triage and automated features."}
               </p>
            </div>

            <div className="space-y-8">
              {/* Identity Profile Content */}
              {activeTab === "Identity Profile" && (
                <>
                  <div className="flex items-center gap-6 p-6 rounded-xl bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700">
                    <div className="w-20 h-20 rounded-full bg-gray-200 dark:bg-gray-700 border-4 border-white dark:border-gray-800 shadow-sm overflow-hidden relative group">
                      <img src={`https://i.pravatar.cc/150?u=${userRole}`} alt="Profile" className="w-full h-full object-cover" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white">{userName || 'Unknown User'}</h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold mt-1">{userRole || 'Role not set'}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Full Name</label>
                      <input 
                        type="text" 
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" 
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Role (Locked)</label>
                      <input type="text" disabled defaultValue={userRole || ''} className="w-full bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-500 px-4 py-2.5 rounded-lg outline-none text-sm cursor-not-allowed uppercase" />
                    </div>
                  </div>
                </>
              )}

              {/* System & Security Content */}
              {activeTab === "System & Security" && (
                <div className="space-y-6">
                  <div className="space-y-4">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                      <Lock size={16} className="text-blue-500" /> Password Management
                    </h3>
                    <div className="grid grid-cols-1 gap-4">
                      <input 
                        type="password" 
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="New Password (leave blank to keep current)" 
                        className="w-full bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white px-4 py-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" 
                      />
                    </div>
                  </div>

                  <div className="pt-6 border-t border-gray-100 dark:border-gray-700 space-y-4">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                      <Smartphone size={16} className="text-blue-500" /> Two-Factor Authentication
                    </h3>
                    <div className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-900/50 border border-gray-200 dark:border-gray-700">
                      <div>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">Require OTP on Login</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Send a code to WhatsApp for every login attempt.</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" defaultChecked className="sr-only peer" />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {/* System Engine Content */}
              {activeTab === "System Engine" && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800/30">
                    <div>
                      <h3 className="text-sm font-bold text-blue-900 dark:text-blue-100 flex items-center gap-2">
                        <Database size={16} /> Norma AI v2.5.0
                      </h3>
                      <p className="text-xs text-blue-700 dark:text-blue-300 mt-1">System is fully updated and operational.</p>
                    </div>
                    <CheckCircle2 size={24} className="text-blue-500" />
                  </div>

                  <div className="pt-4 space-y-4">
                    <h3 className="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                      <Sliders size={16} className="text-blue-500" /> Autonomous Behaviors
                    </h3>
                    
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700">
                        <div>
                          <p className="text-sm font-semibold text-gray-900 dark:text-white">Auto-Assign Appointments</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Allow AI to confirm standard bookings without human review.</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" defaultChecked className="sr-only peer" />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                        </label>
                      </div>

                      <div className="flex items-center justify-between p-4 rounded-xl border border-gray-200 dark:border-gray-700">
                        <div>
                          <p className="text-sm font-semibold text-gray-900 dark:text-white">Smart Triage Escalation</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Instantly alert doctors on urgent keyword detection in WhatsApp.</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input type="checkbox" defaultChecked className="sr-only peer" />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="pt-6 mt-8 border-t border-gray-100 dark:border-gray-700 flex justify-end">
                <button disabled={saving} type="submit" className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-semibold text-sm hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-70">
                  {saving && <Loader2 size={16} className="animate-spin" />}
                  {saving ? 'Saving...' : 'Save Configuration'}
                </button>
              </div>
            </div>
          </form>
        </div>

      </div>
    </motion.div>
  );
}
