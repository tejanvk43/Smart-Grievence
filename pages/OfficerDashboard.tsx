import React, { useState, useEffect } from 'react';
import { User, Complaint, ComplaintStatus, Department } from '../types';
import { api } from '../services/api';
import ComplaintCard from '../components/ComplaintCard';
import StatusBadge from '../components/StatusBadge';
import { Loader2, Brain, TrendingUp, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

interface Props {
  user: User;
}

const OfficerDashboard: React.FC<Props> = ({ user }) => {
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);

  useEffect(() => {
    loadComplaints();
  }, [user]);

  const loadComplaints = async () => {
    setLoading(true);
    const data = await api.getComplaints(user.role, user.department);
    setComplaints(data);
    setLoading(false);
  };

  const handleStatusUpdate = async (newStatus: ComplaintStatus) => {
    if (!selectedComplaint) return;
    
    await api.updateStatus(selectedComplaint.id, newStatus);
    
    // Optimistic update
    const updated = { ...selectedComplaint, status: newStatus };
    setSelectedComplaint(updated);
    setComplaints(prev => prev.map(c => c.id === updated.id ? updated : c));
  };

  return (
    <div className="flex h-[calc(100vh-64px)] overflow-hidden">
      {/* List Column */}
      <div className={`w-full md:w-1/3 lg:w-1/4 border-r border-gray-200 bg-white flex flex-col ${selectedComplaint ? 'hidden md:flex' : 'flex'}`}>
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <h2 className="font-semibold text-gray-900">{user.department} Queue</h2>
          <p className="text-xs text-gray-500 mt-1">{complaints.length} active items</p>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {loading ? (
            <div className="flex justify-center p-8"><Loader2 className="animate-spin text-gray-400" /></div>
          ) : (
            complaints.map(c => (
              <div 
                key={c.id} 
                onClick={() => setSelectedComplaint(c)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${selectedComplaint?.id === c.id ? 'border-primary bg-blue-50' : 'border-gray-100 hover:bg-gray-50'}`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-medium text-sm text-gray-900 line-clamp-1">{c.title}</span>
                  {c.priority === 'High' && <span className="w-2 h-2 rounded-full bg-red-500 mt-1.5 flex-shrink-0"></span>}
                </div>
                <div className="flex justify-between items-center text-xs text-gray-500">
                  <span>{new Date(c.dateSubmitted).toLocaleDateString()}</span>
                  <StatusBadge status={c.status} />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Detail Column */}
      <div className={`flex-1 bg-gray-50 overflow-y-auto ${!selectedComplaint ? 'hidden md:block' : 'block'}`}>
        {selectedComplaint ? (
          <div className="p-6 max-w-4xl mx-auto">
            <button 
              onClick={() => setSelectedComplaint(null)}
              className="md:hidden mb-4 text-sm text-primary font-medium"
            >
              ← Back to List
            </button>

            {/* Header */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <div className="flex flex-col md:flex-row justify-between md:items-start gap-4 mb-6">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h1 className="text-2xl font-bold text-gray-900">{selectedComplaint.title}</h1>
                    <StatusBadge status={selectedComplaint.status} />
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>ID: <span className="font-mono text-gray-700">{selectedComplaint.id}</span></span>
                    <span>•</span>
                    <span>Submitted by {selectedComplaint.userName}</span>
                    <span>•</span>
                    <span>{new Date(selectedComplaint.dateSubmitted).toLocaleString()}</span>
                  </div>
                </div>
                
                <div className="flex gap-2">
                   {selectedComplaint.status !== ComplaintStatus.RESOLVED && (
                     <button 
                        onClick={() => handleStatusUpdate(ComplaintStatus.IN_PROGRESS)}
                        className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50"
                     >
                       Mark In Progress
                     </button>
                   )}
                   {selectedComplaint.status !== ComplaintStatus.RESOLVED && (
                     <button 
                        onClick={() => handleStatusUpdate(ComplaintStatus.RESOLVED)}
                        className="px-4 py-2 bg-secondary text-white rounded-lg text-sm font-medium hover:bg-green-700 shadow-sm"
                     >
                       Resolve
                     </button>
                   )}
                </div>
              </div>

              <div className="prose max-w-none text-gray-800 bg-gray-50 p-4 rounded-lg border border-gray-100">
                {selectedComplaint.description}
              </div>
              
              <div className="mt-4 flex items-center gap-2 text-sm text-gray-600">
                <div className="w-5 h-5 flex items-center justify-center rounded bg-gray-200">📍</div>
                {selectedComplaint.location}
              </div>
            </div>

            {/* AI Analysis Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-4 opacity-5">
                 <Brain size={120} />
               </div>
               
               <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                 <Brain className="text-primary" size={20} />
                 Smart Griev NLP Analysis
               </h3>

               <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                    <div className="text-sm text-blue-600 mb-1">Routed To</div>
                    <div className="font-bold text-gray-900">{selectedComplaint.department}</div>
                    <div className="text-xs text-blue-400 mt-1 flex items-center gap-1">
                      <CheckCircle size={12} /> {(selectedComplaint.nlpAnalysis?.confidenceScore || 0) * 100}% Confidence
                    </div>
                 </div>

                 <div className="p-4 bg-orange-50 rounded-lg border border-orange-100">
                    <div className="text-sm text-orange-600 mb-1">Urgency Level</div>
                    <div className="font-bold text-gray-900 flex items-center gap-2">
                       {selectedComplaint.priority}
                       {selectedComplaint.priority === 'High' && <AlertTriangle size={16} className="text-red-500"/>}
                    </div>
                    <div className="text-xs text-orange-400 mt-1">Based on keyword intensity</div>
                 </div>

                 <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                    <div className="text-sm text-purple-600 mb-1">Detected Keywords</div>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {selectedComplaint.nlpAnalysis?.keywords.map(k => (
                        <span key={k} className="px-2 py-0.5 bg-white rounded border border-purple-200 text-xs font-medium text-purple-700">
                          {k}
                        </span>
                      ))}
                    </div>
                 </div>

                 {/* Suggested Steps */}
                 {selectedComplaint.nlpAnalysis?.suggestedSteps && (
                   <div className="col-span-1 md:col-span-3 p-4 bg-green-50 rounded-lg border border-green-100 mt-2">
                      <div className="text-sm text-green-700 font-bold mb-2 flex items-center gap-2">
                        <CheckCircle size={16} />
                        Recommended Next Steps (AI)
                      </div>
                      <ul className="space-y-1">
                        {selectedComplaint.nlpAnalysis.suggestedSteps.map((step, idx) => (
                          <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                            <span className="mt-1 w-1.5 h-1.5 rounded-full bg-green-500 flex-shrink-0"></span>
                            {step}
                          </li>
                        ))}
                      </ul>
                   </div>
                 )}
               </div>
            </div>

            {/* History/Actions Placeholder */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <Clock className="text-gray-400" size={20} />
                Timeline
              </h3>
              <div className="space-y-6 ml-2 border-l-2 border-gray-100 pl-6 relative">
                 <div className="relative">
                   <div className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-green-500 border-2 border-white"></div>
                   <p className="text-sm font-medium text-gray-900">Complaint Submitted</p>
                   <p className="text-xs text-gray-500">{new Date(selectedComplaint.dateSubmitted).toLocaleString()}</p>
                 </div>
                 {selectedComplaint.status !== ComplaintStatus.SUBMITTED && (
                    <div className="relative">
                      <div className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-blue-500 border-2 border-white"></div>
                      <p className="text-sm font-medium text-gray-900">Assigned to {selectedComplaint.department}</p>
                      <p className="text-xs text-gray-500">Auto-routed via Smart Griev AI</p>
                    </div>
                 )}
                 {selectedComplaint.status === ComplaintStatus.RESOLVED && (
                    <div className="relative">
                      <div className="absolute -left-[31px] top-0 w-4 h-4 rounded-full bg-gray-800 border-2 border-white"></div>
                      <p className="text-sm font-medium text-gray-900">Complaint Resolved</p>
                      <p className="text-xs text-gray-500">{new Date(selectedComplaint.dateUpdated).toLocaleString()}</p>
                    </div>
                 )}
              </div>
            </div>

          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <TrendingUp size={32} />
            </div>
            <p>Select a complaint from the queue to view details.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default OfficerDashboard;