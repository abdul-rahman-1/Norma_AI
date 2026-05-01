import { Outlet, Navigate, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { Search, Bell, Sun, Moon, Loader2, CheckCircle2, AlertCircle, Info } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';

function UserProfile() {
  const { userName, userRole } = useAuth();
  
  const getRoleName = () => {
    if (userRole === 'admin') return 'Administrator';
    if (userRole === 'doctor') return 'Doctor';
    if (userRole === 'receptionist') return 'Receptionist';
    return 'User';
  }

  return (
    <div className="flex items-center gap-4">
      <div className="text-right">
        <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">{userName}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400">{getRoleName()}</p>
      </div>
      <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 border border-gray-300 dark:border-gray-600">
        <img 
          src={`https://i.pravatar.cc/150?u=${userRole}`} 
          alt="Profile" 
          className="w-full h-full object-cover rounded-full" 
        />
      </div>
    </div>
  );
}

export default function Layout() {
  const { isAuthenticated, token, userRole } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Notification state
  const [notifications, setNotifications] = useState<any[]>([]);
  const [showNotifDropdown, setShowNotifDropdown] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchDropdown(false);
      }
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch Notifications for Admin
  useEffect(() => {
    if (userRole === 'admin' && token) {
      const fetchNotifications = async () => {
        try {
          const res = await fetch('/api/dashboard/notifications', {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (res.ok) {
            const data = await res.json();
            setNotifications(data);
          }
        } catch (error) {
          console.error("Failed to fetch notifications", error);
        }
      };
      fetchNotifications();
      // Optional: Poll every minute
      const intervalId = setInterval(fetchNotifications, 60000);
      return () => clearInterval(intervalId);
    }
  }, [userRole, token]);

  // Clear search query when navigating away from search results
  useEffect(() => {
    if (!location.pathname.startsWith('/search')) {
      setSearchQuery('');
      setShowSearchDropdown(false);
    }
  }, [location.pathname]);

  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (searchQuery.length >= 2) {
        setIsSearching(true);
        try {
          const res = await axios.get(`/api/dashboard/search`, {
            params: { q: searchQuery },
            headers: { Authorization: `Bearer ${token}` }
          });
          setSearchResults(res.data);
          setShowSearchDropdown(true);
        } catch (error) {
          console.error("Search failed", error);
        } finally {
          setIsSearching(false);
        }
      } else {
        setSearchResults([]);
        setShowSearchDropdown(false);
      }
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery, token]);

  const handleResultClick = (link: string) => {
    navigate(link);
    setShowSearchDropdown(false);
    setSearchQuery('');
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success': return <CheckCircle2 size={16} className="text-green-500" />;
      case 'error': return <AlertCircle size={16} className="text-red-500" />;
      default: return <Info size={16} className="text-blue-500" />;
    }
  };

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        
        <header className="h-20 flex-shrink-0 bg-white dark:bg-gray-800 flex items-center justify-end px-8 border-b border-gray-200 dark:border-gray-700 transition-colors duration-200 z-50">
          
          <div className="flex items-center gap-6">
            <div className="relative" ref={notifRef}>
              <button 
                onClick={() => setShowNotifDropdown(!showNotifDropdown)}
                className="text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-100 transition-colors duration-200 relative p-1"
                aria-label="Notifications"
              >
                <Bell size={20} />
                {notifications.length > 0 && (
                  <span className="absolute top-0 right-0 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-white dark:border-gray-800"></span>
                )}
              </button>

              {showNotifDropdown && (
                <div className="absolute top-full right-0 mt-4 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl overflow-hidden z-50">
                  <div className="p-4 border-b border-gray-100 dark:border-gray-700">
                    <h3 className="text-sm font-bold text-gray-800 dark:text-gray-200 uppercase tracking-wider">System Alerts</h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.length > 0 ? (
                      notifications.map((notif) => (
                        <div key={notif.id} className="p-4 border-b border-gray-50 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors flex gap-3">
                          <div className="mt-1">{getNotificationIcon(notif.type)}</div>
                          <div>
                            <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">{notif.title}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{notif.message}</p>
                            <p className="text-[10px] text-gray-400 dark:text-gray-500 mt-2 font-medium">{notif.time}</p>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-6 text-center text-sm text-gray-500 dark:text-gray-400">
                        No new notifications
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            <button 
              onClick={toggleTheme}
              className="text-gray-500 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-100 transition-colors duration-200"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            <UserProfile />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-8 scrollbar-thin dark:text-gray-100 relative z-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
