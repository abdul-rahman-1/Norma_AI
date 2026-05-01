import { Link, useLocation } from 'react-router-dom';
import { Home, Calendar, Users, Settings, LogOut, Shield, MessageSquare, Stethoscope, User, Activity, Database, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';

export default function Sidebar() {
  const location = useLocation();
  const { userRole, logout } = useAuth();

  const adminMenuItems = [
    { path: '/admin-dashboard', icon: Shield, label: 'Dashboard' },
    { path: '/doctors', icon: Stethoscope, label: 'Doctors' },
    { path: '/add-doctor', icon: User, label: 'Add Doctor' },
    { path: '/bulk', icon: Database, label: 'Bulk Ingestion' },
    { path: '/knowledge', icon: BookOpen, label: 'Knowledge Base' },
    { path: '/settings', icon: Settings, label: 'System Settings' },
  ];
  
  const doctorMenuItems = [
    { path: '/dashboard', icon: Home, label: 'Overview' },
    { path: '/appointments', icon: Calendar, label: 'Appointments' },
    { path: '/patients', icon: Users, label: 'Patients' },
    { path: '/inbox', icon: MessageSquare, label: 'Inbox' },
    { path: '/add-staff', icon: User, label: 'Manage Staff' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const staffMenuItems = [
    { path: '/dashboard', icon: Home, label: 'Overview' },
    { path: '/appointments', icon: Calendar, label: 'Appointments' },
    { path: '/patients', icon: Users, label: 'Patients' },
    { path: '/inbox', icon: MessageSquare, label: 'Inbox' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  let menuItems = staffMenuItems;
  if (userRole === 'admin') {
    menuItems = adminMenuItems;
  } else if (userRole === 'doctor') {
    menuItems = doctorMenuItems;
  }

  return (
    <aside className="w-64 flex-shrink-0 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-colors duration-200">
      <div className="h-20 flex items-center px-6 border-b border-transparent">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white">
            <Activity size={20} />
          </div>
          <h1 className="text-xl font-extrabold text-gray-800 dark:text-white">Norma AI</h1>
        </div>
      </div>
      
      <nav className="flex-1 px-4 py-4 space-y-2">
        {menuItems.map((item) => {
          const isActive = location.pathname.startsWith(item.path);
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-4 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors duration-200 ${
                isActive
                  ? 'bg-blue-50 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400'
                  : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      
      <div className="p-4">
        <button
          onClick={logout}
          className="w-full flex items-center gap-4 px-4 py-2.5 rounded-lg text-sm font-semibold text-gray-500 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/30 hover:text-red-700 dark:hover:text-red-400 transition-colors duration-200"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
