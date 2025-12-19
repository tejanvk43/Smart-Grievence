import React, { useState } from 'react';
import { User } from './types';
import LandingPage from './pages/LandingPage';
import CitizenDashboard from './pages/CitizenDashboard';
import OfficerDashboard from './pages/OfficerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import { LayoutDashboard, LogOut, Bell, User as UserIcon } from 'lucide-react';

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [view, setView] = useState<'dashboard' | 'notifications' | 'profile'>('dashboard');

  const handleAuthSuccess = (loggedUser: User) => {
    setUser(loggedUser);
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (!user) {
    return <LandingPage onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Sidebar / Mobile Nav */}
      <aside className="w-full md:w-64 bg-white border-r border-gray-200 flex flex-col md:h-screen sticky top-0 z-10">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <div className="flex items-center gap-2 text-primary font-bold text-xl">
            <div className="w-8 h-8 bg-primary text-white rounded flex items-center justify-center text-sm">SG</div>
            Smart Griev
          </div>
          <button className="md:hidden text-gray-500">
             {/* Mobile Menu Icon could go here */}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          <div className="px-4 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Menu
          </div>
          <nav className="space-y-1 px-2">
            <button 
              onClick={() => setView('dashboard')}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${view === 'dashboard' ? 'bg-blue-50 text-primary' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <LayoutDashboard size={18} />
              Dashboard
            </button>
            <button 
              onClick={() => setView('notifications')}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${view === 'notifications' ? 'bg-blue-50 text-primary' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <Bell size={18} />
              Notifications
              {/* <span className="ml-auto bg-red-100 text-red-600 text-xs px-2 py-0.5 rounded-full">3</span> */}
            </button>
            <button 
              onClick={() => setView('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors ${view === 'profile' ? 'bg-blue-50 text-primary' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <UserIcon size={18} />
              Profile
            </button>
          </nav>
        </div>

        <div className="p-4 border-t border-gray-200">
           <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 font-bold">
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{user.name}</p>
                <p className="text-xs text-gray-500 truncate capitalize">{user.role.toLowerCase()}</p>
              </div>
           </div>
           <button 
             onClick={handleLogout}
             className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
           >
             <LogOut size={16} />
             Sign Out
           </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto h-[calc(100vh-64px)] md:h-screen">
        {view === 'dashboard' && (
          <>
            {user.role === 'CITIZEN' && <CitizenDashboard user={user} />}
            {user.role === 'OFFICER' && <OfficerDashboard user={user} />}
            {user.role === 'ADMIN' && <AdminDashboard />}
          </>
        )}
        
        {view === 'notifications' && (
          <div className="p-6 max-w-4xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Notifications</h1>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center text-gray-500">
              <Bell size={48} className="mx-auto mb-4 text-gray-300" />
              <p>No new notifications at this time.</p>
              <p className="text-xs mt-2">Check back later for updates on your complaints.</p>
            </div>
          </div>
        )}

        {view === 'profile' && (
           <div className="p-6 max-w-4xl mx-auto">
             <h1 className="text-2xl font-bold text-gray-900 mb-6">User Profile</h1>
             <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
               <div className="p-6 border-b border-gray-100 bg-gray-50 flex items-center gap-4">
                  <div className="w-20 h-20 rounded-full bg-white border border-gray-200 flex items-center justify-center text-3xl font-bold text-primary shadow-sm">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{user.name}</h2>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {user.role}
                    </span>
                  </div>
               </div>
               <div className="p-6 space-y-4">
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                   <div>
                     <label className="block text-sm font-medium text-gray-500 mb-1">Email Address</label>
                     <div className="text-gray-900 font-medium">{user.email}</div>
                   </div>
                   <div>
                     <label className="block text-sm font-medium text-gray-500 mb-1">Phone Number</label>
                     <div className="text-gray-900 font-medium">{user.phone || 'Not provided'}</div>
                   </div>
                   {user.department && (
                     <div>
                       <label className="block text-sm font-medium text-gray-500 mb-1">Department</label>
                       <div className="text-gray-900 font-medium bg-purple-50 text-purple-700 px-3 py-1 rounded-md inline-block">
                         {user.department}
                       </div>
                     </div>
                   )}
                   <div>
                      <label className="block text-sm font-medium text-gray-500 mb-1">User ID</label>
                      <div className="text-gray-500 font-mono text-xs">{user.id}</div>
                   </div>
                 </div>
               </div>
             </div>
           </div>
        )}
      </main>
    </div>
  );
};

export default App;