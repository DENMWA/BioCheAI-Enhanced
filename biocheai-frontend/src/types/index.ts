export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
}

export interface Analysis {
  id: number;
  user_id: number;
  project_id?: number;
  analysis_type: string;
  title: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  input_data: any;
  results?: any;
  ml_predictions?: any;
  confidence_score?: number;
  police_report?: any;
  compliance_score?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  is_public: boolean;
  created_at: string;
  members?: ProjectMember[];
}

export interface ProjectMember {
  id: number;
  project_id: number;
  user_id: number;
  role: 'owner' | 'admin' | 'member' | 'viewer';
  joined_at: string;
}

export interface LiteratureResult {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  journal: string;
  publication_date: string;
  doi?: string;
  pmid?: string;
  url?: string;
}

export interface Workflow {
  id: number;
  name: string;
  description?: string;
  user_id: number;
  steps: WorkflowStep[];
  template_type?: string;
  created_at: string;
}

export interface WorkflowStep {
  id: number;
  workflow_id: number;
  step_type: string;
  step_name: string;
  parameters: any;
  order_index: number;
}

export interface DataSource {
  id: number;
  name: string;
  source_type: string;
  source_format: string;
  file_path?: string;
  url?: string;
  source_metadata: any;
  schema_info?: any;
  quality_metrics?: any;
  created_at: string;
}

export interface ComplianceReport {
  id: number;
  analysis_id: number;
  framework_type: string;
  compliance_status: string;
  violations: any[];
  recommendations: string[];
  generated_at: string;
}

export interface Repository {
  name: string;
  description: string;
  base_url: string;
  supported_formats: string[];
  rate_limit: string;
  authentication_required: boolean;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

export interface Task {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  status: 'todo' | 'in_progress' | 'completed' | 'blocked';
  priority: 'low' | 'medium' | 'high' | 'critical';
  start_date: string;
  end_date: string;
  estimated_hours: number;
  actual_hours: number;
  progress_percentage: number;
  parent_task_id?: string;
  created_by: number;
  created_at: string;
  updated_at: string;
  assignees: TaskAssignment[];
  dependencies: TaskDependency[];
}

export interface TaskAssignment {
  id: number;
  task_id: string;
  user_id: number;
  role: string;
  hours_allocated: number;
  capacity_percentage: number;
  assigned_at: string;
}

export interface TaskDependency {
  id: number;
  task_id: string;
  depends_on_task_id: string;
  dependency_type: 'finish_to_start' | 'start_to_start' | 'finish_to_finish' | 'start_to_finish';
  lag_days: number;
  created_at: string;
}

export interface Milestone {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  due_date: string;
  status: 'pending' | 'achieved' | 'overdue';
  completion_percentage: number;
  linked_tasks: string[];
  created_by: number;
  created_at: string;
  achieved_at?: string;
}

export interface TimelineData {
  tasks: Task[];
  milestones: Milestone[];
  dependencies: TaskDependency[];
}
