import { Routes, Route, Navigate } from 'react-router-dom';
import AdminLogin from './pages/AdminLogin';
import Login from './pages/Login';
import Layout from './pages/Layout';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import BulkUpload from './pages/BulkUpload';
import Patients from './pages/Patients';
import Doctors from './pages/Doctors';
import Appointments from './pages/Appointments';
import Inbox from './pages/Inbox';
import Settings from './pages/Settings';
import AddDoctor from './pages/AddDoctor';
import AddStaff from './pages/AddStaff';
import SearchResults from './pages/SearchResults';
import KnowledgeBase from './pages/KnowledgeBase';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/admin-login" element={<AdminLogin />} />
      
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        {/* Common for Doctor and Staff */}
        <Route path="/dashboard" element={
          <ProtectedRoute allowedRoles={['doctor', 'staff']}>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/appointments" element={
          <ProtectedRoute allowedRoles={['doctor', 'staff']}>
            <Appointments />
          </ProtectedRoute>
        } />
        <Route path="/patients" element={
          <ProtectedRoute allowedRoles={['doctor', 'staff']}>
            <Patients />
          </ProtectedRoute>
        } />
        <Route path="/inbox" element={
          <ProtectedRoute allowedRoles={['doctor', 'staff']}>
            <Inbox />
          </ProtectedRoute>
        } />
        
        {/* Admin Specific */}
        <Route path="/admin-dashboard" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        } />
        <Route path="/doctors" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <Doctors />
          </ProtectedRoute>
        } />
        <Route path="/add-doctor" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AddDoctor />
          </ProtectedRoute>
        } />
        <Route path="/knowledge" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <KnowledgeBase />
          </ProtectedRoute>
        } />
        
        {/* Doctor and Admin */}
        <Route path="/add-staff" element={
          <ProtectedRoute allowedRoles={['admin', 'doctor']}>
            <AddStaff />
          </ProtectedRoute>
        } />
        <Route path="/bulk" element={
          <ProtectedRoute allowedRoles={['admin', 'doctor']}>
            <BulkUpload />
          </ProtectedRoute>
        } />
        
        {/* All Auth Users */}
        <Route path="/settings" element={
          <ProtectedRoute allowedRoles={['admin', 'doctor', 'staff', 'receptionist']}>
            <Settings />
          </ProtectedRoute>
        } />
        <Route path="/search" element={
          <ProtectedRoute allowedRoles={['admin', 'doctor', 'staff', 'receptionist']}>
            <SearchResults />
          </ProtectedRoute>
        } />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;
