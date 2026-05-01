import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface AuthContextType {
  token: string | null;
  userRole: string | null;
  userName: string | null;
  login: (token: string, role: string, name: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [userRole, setUserRole] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedRole = localStorage.getItem('userRole');
    const storedName = localStorage.getItem('userName');
    if (storedToken && storedRole && storedName) {
      setToken(storedToken);
      setUserRole(storedRole);
      setUserName(storedName);
    }
  }, []);

  const login = (newToken: string, role: string, name: string) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('userRole', role);
    localStorage.setItem('userName', name);
    setToken(newToken);
    setUserRole(role);
    setUserName(name);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userName');
    setToken(null);
    setUserRole(null);
    setUserName(null);
    navigate('/login');
  };

  const value = {
    token,
    userRole,
    userName,
    login,
    logout,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
