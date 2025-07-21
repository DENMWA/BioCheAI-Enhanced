import axios from 'axios';
import { User, Analysis, Project, LiteratureResult, Workflow, DataSource, ComplianceReport, Repository, Task, Milestone, TimelineData } from '../types';

const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: async (username: string, password: string): Promise<{ user: User; access_token: string }> => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  register: async (userData: any): Promise<{ user: User; access_token: string }> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
};

export const analysisApi = {
  create: async (analysisData: any): Promise<Analysis> => {
    const response = await api.post('/analysis', analysisData);
    return response.data.analysis;
  },

  getAll: async (): Promise<Analysis[]> => {
    const response = await api.get('/analyses');
    return response.data.analyses;
  },

  getById: async (id: number): Promise<Analysis> => {
    const response = await api.get(`/analysis/${id}`);
    return response.data.analysis;
  },

  repair: async (id: number): Promise<any> => {
    const response = await api.post(`/analysis/${id}/repair`);
    return response.data;
  },
};

export const dataApi = {
  fetch: async (repository: string, params: any): Promise<any> => {
    const response = await api.post('/data/fetch', { repository, params });
    return response.data;
  },

  getRepositories: async (): Promise<Repository[]> => {
    const response = await api.get('/data/repositories');
    return response.data.repositories;
  },
};

export const literatureApi = {
  search: async (query: string, sources: string[] = ['pubmed'], maxResults: number = 10): Promise<LiteratureResult[]> => {
    const response = await api.post('/literature/search', {
      query,
      sources,
      max_results: maxResults,
    });
    return response.data.results;
  },

  summarize: async (papers: string[]): Promise<string> => {
    const response = await api.post('/literature/summarize', { papers });
    return response.data.summary;
  },

  generateHypotheses: async (literatureIds: string[], researchArea: string): Promise<string[]> => {
    const response = await api.post('/literature/hypotheses', {
      literature_ids: literatureIds,
      research_area: researchArea,
    });
    return response.data.hypotheses;
  },
};

export const projectApi = {
  create: async (projectData: any): Promise<Project> => {
    const response = await api.post('/projects', projectData);
    return response.data.project;
  },

  getAll: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data.projects;
  },
};

export const collaborationApi = {
  createSession: async (projectId: number): Promise<any> => {
    const response = await api.post('/collaboration/sessions', { project_id: projectId });
    return response.data;
  },
};

export const workflowApi = {
  create: async (workflowData: any): Promise<Workflow> => {
    const response = await api.post('/workflows', workflowData);
    return response.data.workflow;
  },

  execute: async (workflowId: number, inputData: any): Promise<any> => {
    const response = await api.post(`/workflows/${workflowId}/execute`, { input_data: inputData });
    return response.data;
  },

  getTemplates: async (): Promise<any[]> => {
    const response = await api.get('/workflow-templates');
    return response.data.templates;
  },
};

export const dataSourceApi = {
  register: async (sourceData: any): Promise<DataSource> => {
    const response = await api.post('/data-sources', sourceData);
    return response.data.data_source;
  },

  createIntegration: async (integrationData: any): Promise<any> => {
    const response = await api.post('/data-integration', integrationData);
    return response.data;
  },
};

export const complianceApi = {
  generateReport: async (analysisId: number, framework: string): Promise<ComplianceReport> => {
    const response = await api.post('/compliance/reports', {
      analysis_id: analysisId,
      framework_type: framework,
    });
    return response.data.report;
  },

  getFrameworks: async (): Promise<string[]> => {
    const response = await api.get('/compliance/frameworks');
    return response.data.frameworks;
  },
};

export const cloudApi = {
  scale: async (analysisId: number, targetInstances: number): Promise<any> => {
    const response = await api.post('/cloud/scale', {
      analysis_id: analysisId,
      target_instances: targetInstances,
    });
    return response.data;
  },

  uploadToCloud: async (file: File, provider: string): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('provider', provider);
    
    const response = await api.post('/cloud/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getStatus: async (): Promise<any> => {
    const response = await api.get('/cloud/status');
    return response.data;
  },
};

export const taskApi = {
  create: async (projectId: string, taskData: any): Promise<Task> => {
    const response = await api.post(`/projects/${projectId}/tasks`, taskData);
    return response.data;
  },

  getAll: async (projectId: string): Promise<Task[]> => {
    const response = await api.get(`/projects/${projectId}/tasks`);
    return response.data.tasks;
  },

  updateProgress: async (taskId: string, progress: number, actualHours?: number): Promise<void> => {
    await api.put(`/tasks/${taskId}/progress`, { progress, actual_hours: actualHours });
  },
};

export const milestoneApi = {
  create: async (projectId: string, milestoneData: any): Promise<Milestone> => {
    const response = await api.post(`/projects/${projectId}/milestones`, milestoneData);
    return response.data;
  },
};

export const timelineApi = {
  getProjectTimeline: async (projectId: string): Promise<TimelineData> => {
    const response = await api.get(`/projects/${projectId}/timeline`);
    return response.data;
  },
};

export default api;
