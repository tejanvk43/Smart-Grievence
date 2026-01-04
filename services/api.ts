import { Complaint, ComplaintStatus, Department, User, UserRole, DashboardStats } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const getAuthToken = (): string | null => {
  return localStorage.getItem('token');
};

const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
};

export const api = {
  login: async (email: string, password: string): Promise<User> => {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }

    const data = await response.json();

    // Store token
    if (data.session?.access_token) {
      localStorage.setItem('token', data.session.access_token);
    }

    return {
      id: data.user.id,
      name: data.user.name,
      email: data.user.email,
      phone: data.user.phone,
      role: data.user.role as UserRole,
      department: data.user.department || undefined
    };
  },

  register: async (name: string, email: string, password: string, role: UserRole, department?: Department): Promise<User> => {
    // Only send department if role is OFFICER
    const payload = {
      name,
      email,
      password,
      role,
      department: role === UserRole.OFFICER ? department : undefined
    };

    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }

    const data = await response.json();

    // Store token
    if (data.session?.access_token) {
      localStorage.setItem('token', data.session.access_token);
    }

    return {
      id: data.user.id,
      name: data.user.name,
      email: data.user.email,
      phone: data.user.phone,
      role: data.user.role as UserRole,
      department: data.user.department || undefined
    };
  },

  logout: () => {
    localStorage.removeItem('token');
    // window.location.reload(); // Optional, let app state handle it
  },

  submitComplaint: async (
    complaintData: Partial<Complaint>,
    user: User
  ): Promise<Complaint> => {
    const headers = getAuthHeaders();

    const response = await fetch(`${API_URL}/complaints/submit`, {
      method: 'POST',
      headers: headers as any,
      body: JSON.stringify({
        title: complaintData.title,
        description: complaintData.description,
        location: complaintData.location
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to submit complaint');
    }

    const data = await response.json();

    return {
      id: data.id,
      userId: data.user_id,
      userName: data.userName || user.name,
      title: data.title,
      description: data.description,
      location: data.location,
      status: data.status as ComplaintStatus,
      department: data.department as Department,
      dateSubmitted: data.date_submitted,
      dateUpdated: data.date_updated,
      priority: data.priority as 'Low' | 'Medium' | 'High',
      attachments: complaintData.attachments || [],
      nlpAnalysis: data.nlp_analysis ? {
        predictedDepartment: data.nlp_analysis.predictedDepartment as Department,
        confidenceScore: data.nlp_analysis.confidenceScore,
        urgency: data.nlp_analysis.urgency,
        keywords: data.nlp_analysis.keywords,
        sentiment: data.nlp_analysis.sentiment,
        suggestedSteps: data.nlp_analysis.suggestedSteps
      } : undefined
    };
  },

  getComplaints: async (role: UserRole, department?: Department): Promise<Complaint[]> => {
    const headers = getAuthHeaders();

    const response = await fetch(`${API_URL}/complaints`, {
      method: 'GET',
      headers: headers as any
    });

    if (!response.ok) {
      if (response.status === 401) {
        localStorage.removeItem('token');
        throw new Error('Session expired. Please login again.');
      }
      throw new Error('Failed to fetch complaints');
    }

    const data = await response.json();

    return data.map((item: any) => ({
      id: item.id,
      userId: item.user_id,
      userName: item.userName || 'Unknown User',
      title: item.title,
      description: item.description,
      location: item.location,
      status: item.status as ComplaintStatus,
      department: item.department as Department,
      dateSubmitted: item.date_submitted,
      dateUpdated: item.date_updated,
      priority: item.priority as 'Low' | 'Medium' | 'High',
      attachments: [],
      nlpAnalysis: item.nlp_analysis ? {
        predictedDepartment: item.nlp_analysis.predictedDepartment as Department,
        confidenceScore: item.nlp_analysis.confidenceScore,
        urgency: item.nlp_analysis.urgency,
        keywords: item.nlp_analysis.keywords,
        sentiment: item.nlp_analysis.sentiment,
        suggestedSteps: item.nlp_analysis.suggestedSteps
      } : undefined
    }));
  },

  updateStatus: async (
    id: string,
    status: ComplaintStatus
  ): Promise<Complaint | undefined> => {
    const headers = getAuthHeaders();

    const response = await fetch(`${API_URL}/complaints/${id}/status`, {
      method: 'PUT',
      headers: headers as any,
      body: JSON.stringify({ status })
    });

    if (!response.ok) {
      throw new Error('Failed to update status');
    }

    const data = await response.json();

    return {
      id: data.id,
      userId: data.user_id,
      userName: data.userName || 'Unknown User',
      title: data.title,
      description: data.description,
      location: data.location,
      status: data.status as ComplaintStatus,
      department: data.department as Department,
      dateSubmitted: data.date_submitted,
      dateUpdated: data.date_updated,
      priority: data.priority as 'Low' | 'Medium' | 'High',
      attachments: [],
      nlpAnalysis: data.nlp_analysis ? {
        predictedDepartment: data.nlp_analysis.predictedDepartment as Department,
        confidenceScore: data.nlp_analysis.confidenceScore,
        urgency: data.nlp_analysis.urgency,
        keywords: data.nlp_analysis.keywords,
        sentiment: data.nlp_analysis.sentiment,
        suggestedSteps: data.nlp_analysis.suggestedSteps
      } : undefined
    };
  },

  getStats: async (): Promise<DashboardStats> => {
    const headers = getAuthHeaders();

    const response = await fetch(`${API_URL}/analytics`, {
      method: 'GET',
      headers: headers as any
    });

    if (!response.ok) {
      throw new Error('Failed to fetch stats');
    }

    return await response.json();
  },

  getDepartments: async (): Promise<any[]> => {
    const response = await fetch(`${API_URL}/departments`, {
      method: 'GET'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch departments');
    }

    return await response.json();
  },

  createOfficer: async (userData: { email: string; password: string; name: string; department: string; phone?: string }): Promise<any> => {
    const headers = getAuthHeaders();

    const response = await fetch(`${API_URL}/admin/users`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      } as any,
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create officer');
    }

    return await response.json();
  }
};
