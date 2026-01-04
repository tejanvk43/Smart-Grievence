import React, { useState } from 'react';
import { UserRole, User } from '../types';
import { api } from '../services/api';
import { Shield, Activity, Users, ArrowRight, Loader2 } from 'lucide-react';

interface Props {
  onAuthSuccess: (user: User) => void;
}

const LandingPage: React.FC<Props> = ({ onAuthSuccess }) => {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState<UserRole>(UserRole.CITIZEN);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let user;
      if (isRegistering) {
        user = await api.register(name, email, password, role);
      } else {
        user = await api.login(email, password);
      }
      onAuthSuccess(user);
    } catch (error: any) {
      console.error("Auth failed", error);
      setError(error.message || 'Authentication failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsRegistering(!isRegistering);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold">
            SG
          </div>
          <span className="text-xl font-bold text-gray-900">Smart Griev</span>
        </div>
        <div className="hidden md:flex gap-6 text-sm font-medium text-gray-600">
          <a href="#" className="hover:text-primary" onClick={(e) => e.preventDefault()}>How it Works</a>
          <a href="#" className="hover:text-primary" onClick={(e) => e.preventDefault()}>Departments</a>
          <a href="#" className="hover:text-primary" onClick={(e) => e.preventDefault()}>Contact</a>
        </div>
      </nav>

      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Left Side - Hero */}
        <div className="lg:w-1/2 p-8 lg:p-16 flex flex-col justify-center">
          <div className="max-w-xl mx-auto lg:mx-0">
            <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold mb-6">
              AI-Powered Citizen Services
            </span>
            <h1 className="text-4xl lg:text-6xl font-extrabold text-gray-900 mb-6 leading-tight">
              Grievance Redressal, <span className="text-primary">Simplified.</span>
            </h1>
            <p className="text-lg text-gray-600 mb-8 leading-relaxed">
              Don't know which department to approach? Just tell us your problem. 
              Our AI automatically analyzes your complaint and routes it to the right officer instantly.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="flex flex-col gap-2">
                <div className="w-10 h-10 bg-green-100 text-green-600 rounded-lg flex items-center justify-center">
                  <Activity size={20} />
                </div>
                <h3 className="font-bold text-gray-900">Fast Resolution</h3>
                <p className="text-sm text-gray-500">Auto-routing cuts delays by 40%</p>
              </div>
              <div className="flex flex-col gap-2">
                <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center">
                  <Shield size={20} />
                </div>
                <h3 className="font-bold text-gray-900">Transparent</h3>
                <p className="text-sm text-gray-500">Track status in real-time</p>
              </div>
              <div className="flex flex-col gap-2">
                <div className="w-10 h-10 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center">
                  <Users size={20} />
                </div>
                <h3 className="font-bold text-gray-900">Accessible</h3>
                <p className="text-sm text-gray-500">Easy for everyone to use</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side - Auth Form */}
        <div className="lg:w-1/2 bg-white flex flex-col justify-center p-8 lg:p-16 border-l border-gray-100">
          <div className="max-w-md mx-auto w-full">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900">
                {isRegistering ? 'Create Account' : 'Sign in to Portal'}
              </h2>
              <p className="text-gray-500 mt-2">Select your role to continue</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-3 gap-2 p-1 bg-gray-100 rounded-lg mb-6">
                {[UserRole.CITIZEN, UserRole.OFFICER, UserRole.ADMIN].map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setRole(r)}
                    className={`text-sm font-medium py-2 rounded-md transition-all capitalize ${
                      role === r ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    }`}
                    disabled={isRegistering}
                  >
                    {r.toLowerCase()}
                  </button>
                ))}
              </div>

              {isRegistering && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <input
                    type="text"
                    required={isRegistering}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                    placeholder="John Doe"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                  placeholder="name@example.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={6}
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                  placeholder="••••••••"
                />
                {!isRegistering && (
                  <div className="flex justify-end mt-1">
                    <a href="#" onClick={(e) => e.preventDefault()} className="text-xs text-primary hover:underline">Forgot password?</a>
                  </div>
                )}
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-primary hover:bg-blue-700 text-white font-bold py-3 rounded-lg shadow-sm transition-all flex items-center justify-center gap-2 disabled:opacity-70"
              >
                {loading ? <Loader2 className="animate-spin" /> : (
                  <>
                    {isRegistering ? 'Register' : 'Sign In'} <ArrowRight size={18} />
                  </>
                )}
              </button>
            </form>
            
            <div className="mt-8 text-center text-sm text-gray-500">
              {isRegistering ? "Already have an account?" : "Don't have an account?"}{' '}
              <a href="#" onClick={toggleMode} className="text-primary font-bold hover:underline">
                {isRegistering ? 'Sign In' : 'Register Now'}
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;