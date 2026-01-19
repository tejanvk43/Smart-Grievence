import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { DashboardStats, User } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, FileText, CheckSquare, Activity, UserPlus, X, Shield } from 'lucide-react';

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [showOfficerModal, setShowOfficerModal] = useState(false);
  const [departments, setDepartments] = useState<string[]>([]);
  const [officers, setOfficers] = useState<User[]>([]);
  const [loadingOfficers, setLoadingOfficers] = useState(false);
  const [officerForm, setOfficerForm] = useState({
    email: '',
    password: '',
    name: '',
    department: '',
    phone: ''
  });
  const [formMessage, setFormMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const fetchStats = async () => {
      const data = await api.getStats();
      setStats(data);
    };
    fetchStats();
    loadOfficers();
  }, []);

  const loadOfficers = async () => {
    setLoadingOfficers(true);
    try {
      const allUsers = await api.getAllUsers();
      const officerList = allUsers.filter((u: User) => u.role === 'OFFICER');
      setOfficers(officerList);
    } catch (error) {
      console.error('Failed to fetch officers:', error);
    } finally {
      setLoadingOfficers(false);
    }
  };

  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const depts = await api.getDepartments();
        setDepartments(depts);
      } catch (error) {
        console.error('Failed to fetch departments:', error);
      }
    };
    fetchDepartments();
  }, []);

  const handleCreateOfficer = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormMessage({ type: '', text: '' });

    try {
      await api.createOfficer(officerForm);
      setFormMessage({ type: 'success', text: 'Officer created successfully!' });
      setOfficerForm({ email: '', password: '', name: '', department: '', phone: '' });
      loadOfficers(); // Reload officers list
      setTimeout(() => {
        setShowOfficerModal(false);
        setFormMessage({ type: '', text: '' });
      }, 2000);
    } catch (error: any) {
      setFormMessage({ type: 'error', text: error.message || 'Failed to create officer' });
    }
  };

  // Mock data for charts
  const deptData = [
    { name: 'Public Works', value: 35 },
    { name: 'Water', value: 25 },
    { name: 'Electric', value: 20 },
    { name: 'Health', value: 10 },
    { name: 'Others', value: 10 },
  ];

  const statusData = [
    { name: 'Mon', submitted: 4, resolved: 2 },
    { name: 'Tue', submitted: 3, resolved: 4 },
    { name: 'Wed', submitted: 7, resolved: 5 },
    { name: 'Thu', submitted: 2, resolved: 3 },
    { name: 'Fri', submitted: 6, resolved: 6 },
    { name: 'Sat', submitted: 1, resolved: 0 },
    { name: 'Sun', submitted: 2, resolved: 1 },
  ];

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">System Overview</h1>
        <button
          onClick={() => setShowOfficerModal(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <UserPlus size={20} />
          Create Officer
        </button>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
            <FileText size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Total Complaints</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.total || '-'}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-yellow-50 text-yellow-600 rounded-lg">
            <Activity size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Pending</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.pending || '-'}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-green-50 text-green-600 rounded-lg">
            <CheckSquare size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Resolved</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.resolved || '-'}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 bg-purple-50 text-purple-600 rounded-lg">
            <Users size={24} />
          </div>
          <div>
            <p className="text-sm text-gray-500">Avg Resolution</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.avgResolutionTime || '-'}</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-[400px]">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Department Distribution</h2>
          <ResponsiveContainer width="100%" height="90%">
            <PieChart>
              <Pie
                data={deptData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                fill="#8884d8"
                paddingAngle={5}
                dataKey="value"
              >
                {deptData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-[400px]">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Weekly Trends</h2>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart
              data={statusData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" axisLine={false} tickLine={false} />
              <YAxis axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: '#f3f4f6' }} />
              <Legend />
              <Bar dataKey="submitted" fill="#1976d2" radius={[4, 4, 0, 0]} name="New Complaints" />
              <Bar dataKey="resolved" fill="#4caf50" radius={[4, 4, 0, 0]} name="Resolved" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      <div className="mt-8 bg-blue-900 text-white p-6 rounded-xl flex justify-between items-center">
        <div>
           <h3 className="font-bold text-lg">AI Model Performance</h3>
           <p className="text-blue-200">Current routing accuracy based on user feedback</p>
        </div>
        <div className="text-4xl font-bold text-green-400">92.4%</div>
      </div>

      {/* Officers List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Shield size={20} className="text-indigo-600" />
            Registered Officers
          </h2>
          <span className="text-sm text-gray-500">{officers.length} total</span>
        </div>

        {loadingOfficers ? (
          <div className="text-center py-8">
            <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="text-gray-500 mt-2">Loading officers...</p>
          </div>
        ) : officers.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Shield size={48} className="mx-auto mb-2 text-gray-300" />
            <p>No officers created yet.</p>
            <p className="text-sm">Click "Create Officer" to add one.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Name</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Email</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Department</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Phone</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {officers.map((officer) => (
                  <tr key={officer.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-indigo-100 text-indigo-600 rounded-full flex items-center justify-center text-sm font-medium">
                          {officer.name.charAt(0).toUpperCase()}
                        </div>
                        <span className="font-medium text-gray-900">{officer.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{officer.email}</td>
                    <td className="px-4 py-3">
                      <span className="inline-block bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs font-medium">
                        {officer.department}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{officer.phone || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Officer Modal */}
      {showOfficerModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Create Officer Account</h2>
              <button
                onClick={() => {
                  setShowOfficerModal(false);
                  setFormMessage({ type: '', text: '' });
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>

            <form onSubmit={handleCreateOfficer} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                <input
                  type="text"
                  required
                  value={officerForm.name}
                  onChange={(e) => setOfficerForm({ ...officerForm, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address *</label>
                <input
                  type="email"
                  required
                  value={officerForm.email}
                  onChange={(e) => setOfficerForm({ ...officerForm, email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="officer@department.gov"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                <input
                  type="password"
                  required
                  value={officerForm.password}
                  onChange={(e) => setOfficerForm({ ...officerForm, password: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="Minimum 8 characters"
                  minLength={8}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Department *</label>
                <select
                  required
                  value={officerForm.department}
                  onChange={(e) => setOfficerForm({ ...officerForm, department: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                >
                  <option value="">Select Department</option>
                  {departments.map((dept) => (
                    <option key={dept} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                <input
                  type="tel"
                  value={officerForm.phone}
                  onChange={(e) => setOfficerForm({ ...officerForm, phone: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none"
                  placeholder="+1 (555) 000-0000"
                />
              </div>

              {formMessage.text && (
                <div className={`p-3 rounded-lg text-sm ${
                  formMessage.type === 'success' 
                    ? 'bg-green-50 text-green-800' 
                    : 'bg-red-50 text-red-800'
                }`}>
                  {formMessage.text}
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowOfficerModal(false);
                    setFormMessage({ type: '', text: '' });
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Create Officer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;