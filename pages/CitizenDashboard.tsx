import React, { useState, useEffect } from 'react';
import { User, Complaint } from '../types';
import { api } from '../services/api';
import ComplaintCard from '../components/ComplaintCard';
import StatusBadge from '../components/StatusBadge';
import { Plus, List, MapPin, Upload, X, Loader2, Calendar, AlertCircle } from 'lucide-react';

interface Props {
  user: User;
}

const CitizenDashboard: React.FC<Props> = ({ user }) => {
  const [activeTab, setActiveTab] = useState<'submit' | 'list'>('list');
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  
  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadComplaints();
  }, []);

  const loadComplaints = async () => {
    setLoading(true);
    const data = await api.getComplaints(user.role);
    setComplaints(data);
    setLoading(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitSuccess(null);

    // Simulate sending data to backend
    const newComplaint = await api.submitComplaint({
      title,
      description,
      location,
      attachments: files.map(f => f.name)
    }, user);

    setIsSubmitting(false);
    setSubmitSuccess(newComplaint.id);
    
    // Reset form
    setTitle('');
    setDescription('');
    setLocation('');
    setFiles([]);
    
    // Refresh list
    loadComplaints();
  };

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-6">
      <div className="flex flex-col md:flex-row justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome, {user.name}</h1>
          <p className="text-gray-500">Manage your grievances and track their status</p>
        </div>
        <button 
          onClick={() => {
            setActiveTab('submit');
            setSubmitSuccess(null);
          }}
          className="mt-4 md:mt-0 bg-primary hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 shadow-sm transition-colors"
        >
          <Plus size={20} />
          New Complaint
        </button>
      </div>

      <div className="flex gap-6 mb-6 border-b border-gray-200">
        <button 
          className={`pb-3 px-1 text-sm font-medium transition-colors border-b-2 ${activeTab === 'list' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('list')}
        >
          My Complaints
        </button>
        <button 
          className={`pb-3 px-1 text-sm font-medium transition-colors border-b-2 ${activeTab === 'submit' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
          onClick={() => setActiveTab('submit')}
        >
          Submit New
        </button>
      </div>

      {activeTab === 'list' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
             <div className="col-span-full flex justify-center py-12">
               <Loader2 className="animate-spin text-primary" size={32} />
             </div>
          ) : complaints.length === 0 ? (
            <div className="col-span-full text-center py-12 bg-white rounded-lg border border-dashed border-gray-300">
              <p className="text-gray-500">No complaints found. Submit your first one!</p>
            </div>
          ) : (
            complaints.map(c => (
              <ComplaintCard 
                key={c.id} 
                complaint={c} 
                role={user.role} 
                onClick={() => setSelectedComplaint(c)}
              />
            ))
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 max-w-2xl mx-auto">
          {submitSuccess ? (
            <div className="text-center py-8">
              <div className="bg-green-100 text-green-600 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Plus size={32} />
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">Complaint Submitted!</h2>
              <p className="text-gray-600 mb-6">
                Your complaint ID is <span className="font-mono font-bold text-gray-900">{submitSuccess}</span>.<br/>
                We have automatically routed it to the relevant department based on your description.
              </p>
              <button 
                onClick={() => setActiveTab('list')}
                className="text-primary font-medium hover:underline"
              >
                View Status →
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                <input 
                  type="text" 
                  required
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                  placeholder="Brief summary of the issue"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Detailed Description</label>
                <div className="relative">
                  <textarea 
                    required
                    value={description}
                    onChange={e => setDescription(e.target.value)}
                    rows={5}
                    className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none"
                    placeholder="Describe the issue in detail. Our AI will analyze this to identify the department and urgency."
                  />
                  <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                    AI Analysis Enabled
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-2.5 text-gray-400" size={18} />
                    <input 
                      type="text" 
                      required
                      value={location}
                      onChange={e => setLocation(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
                      placeholder="Street, Landmark, Area"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Attachments (Optional)</label>
                  <div className="relative">
                    <input 
                      type="file" 
                      multiple
                      onChange={handleFileChange}
                      className="hidden" 
                      id="file-upload"
                    />
                    <label 
                      htmlFor="file-upload"
                      className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg border border-dashed border-gray-300 text-gray-600 hover:bg-gray-50 cursor-pointer transition-colors"
                    >
                      <Upload size={18} />
                      <span>{files.length > 0 ? `${files.length} files selected` : 'Upload Photos/Docs'}</span>
                    </label>
                  </div>
                </div>
              </div>

              <div className="pt-4 flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => setActiveTab('list')}
                  className="px-6 py-2 rounded-lg text-gray-600 hover:bg-gray-100 font-medium"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="bg-primary hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium shadow-sm transition-all flex items-center gap-2 disabled:opacity-70"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="animate-spin" size={18} />
                      Analyzing & Submitting...
                    </>
                  ) : 'Submit Complaint'}
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Complaint Detail Modal */}
      {selectedComplaint && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onClick={() => setSelectedComplaint(null)}>
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6 border-b border-gray-200 flex justify-between items-start">
              <div>
                <span className="text-xs text-gray-500 font-mono">#{selectedComplaint.id}</span>
                <h2 className="text-2xl font-bold text-gray-900 mt-1">{selectedComplaint.title}</h2>
              </div>
              <button onClick={() => setSelectedComplaint(null)} className="text-gray-400 hover:text-gray-600">
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Description</h3>
                <p className="text-gray-600">{selectedComplaint.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Status</h3>
                  <StatusBadge status={selectedComplaint.status} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Priority</h3>
                  <span className={`inline-flex items-center gap-1 text-sm font-medium ${selectedComplaint.priority === 'High' ? 'text-red-600' : 'text-gray-600'}`}>
                    <AlertCircle size={16} />
                    {selectedComplaint.priority}
                  </span>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-1">Location</h3>
                <div className="flex items-center gap-2 text-gray-600">
                  <MapPin size={16} />
                  <span>{selectedComplaint.location}</span>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-1">Department</h3>
                <span className="inline-block bg-blue-50 text-blue-700 px-3 py-1 rounded-lg text-sm">
                  {selectedComplaint.department}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Submitted</h3>
                  <div className="flex items-center gap-2 text-gray-600 text-sm">
                    <Calendar size={16} />
                    <span>{new Date(selectedComplaint.dateSubmitted).toLocaleString()}</span>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Last Updated</h3>
                  <div className="flex items-center gap-2 text-gray-600 text-sm">
                    <Calendar size={16} />
                    <span>{new Date(selectedComplaint.dateUpdated).toLocaleString()}</span>
                  </div>
                </div>
              </div>
              
              {selectedComplaint.nlpAnalysis && (
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">AI Analysis</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Confidence Score:</span>
                      <span className="font-medium text-primary">
                        {Math.round(selectedComplaint.nlpAnalysis.confidenceScore * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Urgency:</span>
                      <span className="font-medium">{selectedComplaint.nlpAnalysis.urgency}</span>
                    </div>
                    {selectedComplaint.nlpAnalysis.keywords && selectedComplaint.nlpAnalysis.keywords.length > 0 && (
                      <div>
                        <span className="text-gray-600">Keywords:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {selectedComplaint.nlpAnalysis.keywords.map((keyword, idx) => (
                            <span key={idx} className="bg-white text-blue-700 px-2 py-0.5 rounded text-xs">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            <div className="p-6 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => setSelectedComplaint(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CitizenDashboard;