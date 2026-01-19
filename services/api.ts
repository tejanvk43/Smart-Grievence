import { Complaint, ComplaintStatus, Department, User, UserRole, DashboardStats } from '../types';

// Detect environment and set appropriate API URL
function getApiUrl(): string {
  // Check if explicitly set in env
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  
  // Check if running in GitHub Codespaces
  const hostname = window.location.hostname;
  if (hostname.includes('github.dev') || hostname.includes('app.github.dev')) {
    // In Codespaces, construct the backend URL using the same domain but different port
    // Frontend runs on one port, backend on 8000
    const protocol = window.location.protocol;
    const baseUrl = hostname.replace(/-\d+\./, '-8000.');
    return `${protocol}//${baseUrl}/api`;
  }
  
  // Default to localhost
  return 'http://localhost:8000/api';
}

const API_URL = getApiUrl();

// Log API URL for debugging
console.log('🔗 API URL:', API_URL);

// Retry configuration
interface RetryConfig {
  maxRetries: number;
  retryableStatuses: number[];
  baseDelay: number;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryableStatuses: [408, 429, 500, 502, 503, 504],
  baseDelay: 1000
};

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

/**
 * Fetch with exponential backoff retry logic
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  config: RetryConfig = DEFAULT_RETRY_CONFIG
): Promise<Response> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      
      // Don't retry on success or client errors (4xx), except for rate limiting
      if (response.ok || (response.status >= 400 && response.status < 500 && response.status !== 429)) {
        return response;
      }
      
      // Retry on server errors and rate limiting
      if (config.retryableStatuses.includes(response.status) && attempt < config.maxRetries) {
        const delay = config.baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      
      return response;
    } catch (error) {
      lastError = error as Error;
      if (attempt < config.maxRetries) {
        const delay = config.baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
    }
  }
  
  throw lastError || new Error('Max retries exceeded');
}

export const api = {
  login: async (email: string, password: string): Promise<User> => {
    const response = await fetchWithRetry(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      if (response.status === 401) {
        throw new Error(error.message || 'Invalid email or password');
      }
      throw new Error(error.message || 'Login failed');
    }

    const data = await response.json();

    // Store token
    if (data.data?.session?.access_token) {
      localStorage.setItem('token', data.data.session.access_token);
    } else if (data.session?.access_token) {
      localStorage.setItem('token', data.session.access_token);
    }

    const userData = data.data?.user || data.user;
    return {
      id: userData.id,
      name: userData.name,
      email: userData.email,
      phone: userData.phone,
      role: userData.role as UserRole,
      department: userData.department || undefined
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

    const response = await fetchWithRetry(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      if (response.status === 409) {
        throw new Error('User already exists');
      }
      throw new Error(error.message || 'Registration failed');
    }

    const data = await response.json();

    // Store token
    if (data.data?.session?.access_token) {
      localStorage.setItem('token', data.data.session.access_token);
    } else if (data.session?.access_token) {
      localStorage.setItem('token', data.session.access_token);
    }

    const userData = data.data?.user || data.user;
    return {
      id: userData.id,
      name: userData.name,
      email: userData.email,
      phone: userData.phone,
      role: userData.role as UserRole,
      department: userData.department || undefined
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

    const response = await fetchWithRetry(`${API_URL}/complaints/submit`, {
      method: 'POST',
      headers: headers as any,
      body: JSON.stringify({
        title: complaintData.title,
        description: complaintData.description,
        location: complaintData.location
      })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'Failed to submit complaint');
    }

    const data = await response.json();
    const complaintData_ = data.data || data;

    return {
      id: complaintData_.id,
      userId: complaintData_.user_id,
      userName: complaintData_.userName || user.name,
      title: complaintData_.title,
      description: complaintData_.description,
      location: complaintData_.location,
      status: complaintData_.status as ComplaintStatus,
      department: complaintData_.department as Department,
      dateSubmitted: complaintData_.date_submitted,
      dateUpdated: complaintData_.date_updated,
      priority: complaintData_.priority as 'Low' | 'Medium' | 'High',
      attachments: complaintData.attachments || [],
      nlpAnalysis: complaintData_.nlp_analysis ? {
        predictedDepartment: complaintData_.nlp_analysis.predictedDepartment as Department,
        confidenceScore: complaintData_.nlp_analysis.confidenceScore,
        urgency: complaintData_.nlp_analysis.urgency,
        keywords: complaintData_.nlp_analysis.keywords,
        sentiment: complaintData_.nlp_analysis.sentiment,
        suggestedSteps: complaintData_.nlp_analysis.suggestedSteps
      } : undefined
    };
  },

  getComplaints: async (role: UserRole, department?: Department): Promise<Complaint[]> => {
    const headers = getAuthHeaders();

    const response = await fetchWithRetry(`${API_URL}/complaints`, {
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
    const complaintsArray = data.data || data;

    return complaintsArray.map((item: any) => ({
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

    const response = await fetchWithRetry(`${API_URL}/complaints/${id}/status`, {
      method: 'PUT',
      headers: headers as any,
      body: JSON.stringify({ status })
    });

    if (!response.ok) {
      throw new Error('Failed to update status');
    }

    const data = await response.json();
    const complaintData_ = data.data || data;

    return {
      id: complaintData_.id,
      userId: complaintData_.user_id,
      userName: complaintData_.userName || 'Unknown User',
      title: complaintData_.title,
      description: complaintData_.description,
      location: complaintData_.location,
      status: complaintData_.status as ComplaintStatus,
      department: complaintData_.department as Department,
      dateSubmitted: complaintData_.date_submitted,
      dateUpdated: complaintData_.date_updated,
      priority: complaintData_.priority as 'Low' | 'Medium' | 'High',
      attachments: [],
      nlpAnalysis: complaintData_.nlp_analysis ? {
        predictedDepartment: complaintData_.nlp_analysis.predictedDepartment as Department,
        confidenceScore: complaintData_.nlp_analysis.confidenceScore,
        urgency: complaintData_.nlp_analysis.urgency,
        keywords: complaintData_.nlp_analysis.keywords,
        sentiment: complaintData_.nlp_analysis.sentiment,
        suggestedSteps: complaintData_.nlp_analysis.suggestedSteps
      } : undefined
    };
  },

  getStats: async (): Promise<DashboardStats> => {
    const headers = getAuthHeaders();

    const response = await fetchWithRetry(`${API_URL}/analytics`, {
      method: 'GET',
      headers: headers as any
    });

    if (!response.ok) {
      throw new Error('Failed to fetch stats');
    }

    const data = await response.json();
    return data.data || data;
  },

  getDepartments: async (): Promise<any[]> => {
    const response = await fetchWithRetry(`${API_URL}/departments`, {
      method: 'GET'
    });

    if (!response.ok) {
      throw new Error('Failed to fetch departments');
    }

    const data = await response.json();
    return data.data || data;
  },

  getAllUsers: async (): Promise<User[]> => {
    const headers = getAuthHeaders();

    const response = await fetchWithRetry(`${API_URL}/admin/users`, {
      method: 'GET',
      headers: headers as any
    });

    if (!response.ok) {
      throw new Error('Failed to fetch users');
    }

    const data = await response.json();
    const users = data.data || data;
    
    return users.map((u: any) => ({
      id: u.id,
      name: u.name,
      email: u.email,
      phone: u.phone || '',
      role: u.role as UserRole,
      department: u.department,
      createdAt: u.created_at
    }));
  },

  createOfficer: async (userData: { email: string; password: string; name: string; department: string; phone?: string }): Promise<any> => {
    const headers = getAuthHeaders();

    const response = await fetchWithRetry(`${API_URL}/admin/users`, {
      method: 'POST',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      } as any,
      body: JSON.stringify(userData)
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || 'Failed to create officer');
    }

    const data = await response.json();
    return data.data || data;
  }
};
