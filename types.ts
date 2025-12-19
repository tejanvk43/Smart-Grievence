export enum UserRole {
  CITIZEN = 'CITIZEN',
  OFFICER = 'OFFICER',
  ADMIN = 'ADMIN'
}

export enum ComplaintStatus {
  SUBMITTED = 'Submitted',
  ASSIGNED = 'Assigned',
  IN_PROGRESS = 'In Progress',
  RESOLVED = 'Resolved',
  CLOSED = 'Closed',
  REJECTED = 'Rejected'
}

export enum Department {
  PUBLIC_WORKS = 'Public Works & Infrastructure',
  WATER_SUPPLY = 'Water Supply & Sanitation',
  ELECTRICITY = 'Electricity & Power',
  TRANSPORTATION = 'Transportation',
  HEALTH = 'Health & Medical Services',
  EDUCATION = 'Education',
  POLICE = 'Police & Safety',
  REVENUE = 'Revenue & Tax',
  ENVIRONMENT = 'Environment & Pollution',
  CONSUMER = 'Consumer Affairs',
  OTHER = 'Others'
}

export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: UserRole;
  department?: Department; // Only for officers
}

export interface NLPAnalysis {
  predictedDepartment: Department;
  confidenceScore: number;
  urgency: 'Low' | 'Medium' | 'High';
  keywords: string[];
  sentiment: 'Positive' | 'Neutral' | 'Negative';
  suggestedSteps?: string[];
}

export interface Complaint {
  id: string;
  userId: string;
  userName: string;
  title: string;
  description: string;
  location: string;
  status: ComplaintStatus;
  department: Department;
  dateSubmitted: string;
  dateUpdated: string;
  nlpAnalysis?: NLPAnalysis;
  priority: 'Low' | 'Medium' | 'High';
  attachments: string[];
}

export interface DashboardStats {
  total: number;
  pending: number;
  resolved: number;
  avgResolutionTime: string; // e.g., "2.4 days"
}