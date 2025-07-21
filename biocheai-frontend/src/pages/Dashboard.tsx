import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { analysisApi, projectApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Database,
  BookOpen,
  Users,
  Workflow,
  Layers,
  Shield,
  Cloud,
  TrendingUp,
  Activity,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  const { data: analyses = [], isLoading: analysesLoading } = useQuery({
    queryKey: ['analyses'],
    queryFn: analysisApi.getAll,
  });

  const { data: projects = [], isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.getAll,
  });

  const recentAnalyses = analyses.slice(0, 5);
  const recentProjects = projects.slice(0, 3);

  const analysisStatusData = [
    { name: 'Completed', value: analyses.filter(a => a.status === 'completed').length, color: '#10b981' },
    { name: 'Running', value: analyses.filter(a => a.status === 'running').length, color: '#3b82f6' },
    { name: 'Failed', value: analyses.filter(a => a.status === 'failed').length, color: '#ef4444' },
    { name: 'Pending', value: analyses.filter(a => a.status === 'pending').length, color: '#f59e0b' },
  ];

  const analysisTypeData = analyses.reduce((acc: any[], analysis) => {
    const existing = acc.find(item => item.name === analysis.analysis_type);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ name: analysis.analysis_type, count: 1 });
    }
    return acc;
  }, []);

  const features = [
    {
      name: 'Data Fetching',
      description: 'Fetch data from NCBI, Ensembl, UniProt, and more',
      icon: Database,
      href: '/data-fetching',
      color: 'bg-blue-500',
    },
    {
      name: 'Literature Intelligence',
      description: 'AI-powered literature search and analysis',
      icon: BookOpen,
      href: '/literature',
      color: 'bg-green-500',
    },
    {
      name: 'Collaboration',
      description: 'Real-time project collaboration and sharing',
      icon: Users,
      href: '/projects',
      color: 'bg-purple-500',
    },
    {
      name: 'Workflow Builder',
      description: 'No-code analysis pipeline creation',
      icon: Workflow,
      href: '/workflows',
      color: 'bg-orange-500',
    },
    {
      name: 'Data Integration',
      description: 'Multi-modal data integration and harmonization',
      icon: Layers,
      href: '/data-integration',
      color: 'bg-teal-500',
    },
    {
      name: 'Compliance',
      description: 'Regulatory compliance and reporting',
      icon: Shield,
      href: '/compliance',
      color: 'bg-red-500',
    },
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'running':
        return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      completed: 'default',
      running: 'secondary',
      failed: 'destructive',
      pending: 'outline',
    };
    return variants[status] || 'outline';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-600 mt-1">
            Here's what's happening with your research today.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analyses.length}</div>
            <p className="text-xs text-muted-foreground">
              {analyses.filter(a => a.status === 'completed').length} completed
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Projects</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{projects.length}</div>
            <p className="text-xs text-muted-foreground">
              {projects.filter(p => p.is_public).length} public projects
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analyses.length > 0 
                ? Math.round((analyses.reduce((acc, a) => acc + (a.compliance_score || 0), 0) / analyses.length) * 100)
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              Average across all analyses
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cloud Resources</CardTitle>
            <Cloud className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analyses.filter(a => a.status === 'running').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Active cloud instances
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Analysis Status Distribution</CardTitle>
            <CardDescription>Overview of your analysis pipeline</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={analysisStatusData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {analysisStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Analysis Types</CardTitle>
            <CardDescription>Distribution of analysis types</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={analysisTypeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Card key={feature.name} className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link to={feature.href}>
              <CardHeader>
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${feature.color}`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{feature.name}</CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription>{feature.description}</CardDescription>
              </CardContent>
            </Link>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Analyses</CardTitle>
            <CardDescription>Your latest analysis runs</CardDescription>
          </CardHeader>
          <CardContent>
            {analysesLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : recentAnalyses.length > 0 ? (
              <div className="space-y-4">
                {recentAnalyses.map((analysis) => (
                  <div key={analysis.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(analysis.status)}
                      <div>
                        <Link 
                          to={`/analysis/${analysis.id}`}
                          className="font-medium text-gray-900 hover:text-blue-600"
                        >
                          {analysis.title}
                        </Link>
                        <p className="text-sm text-gray-500">{analysis.analysis_type}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant={getStatusBadge(analysis.status)}>
                        {analysis.status}
                      </Badge>
                      {analysis.compliance_score && (
                        <span className="text-sm text-gray-500">
                          {Math.round(analysis.compliance_score * 100)}%
                        </span>
                      )}
                    </div>
                  </div>
                ))}
                <div className="pt-2">
                  <Link to="/data-fetching">
                    <Button variant="outline" className="w-full">
                      View All Analyses
                    </Button>
                  </Link>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <Database className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No analyses yet</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by creating your first analysis.</p>
                <div className="mt-6">
                  <Link to="/data-fetching">
                    <Button>Create Analysis</Button>
                  </Link>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Active Projects</CardTitle>
            <CardDescription>Your collaborative research projects</CardDescription>
          </CardHeader>
          <CardContent>
            {projectsLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                ))}
              </div>
            ) : recentProjects.length > 0 ? (
              <div className="space-y-4">
                {recentProjects.map((project) => (
                  <div key={project.id} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">{project.name}</h4>
                      <Badge variant={project.is_public ? "default" : "secondary"}>
                        {project.is_public ? "Public" : "Private"}
                      </Badge>
                    </div>
                    {project.description && (
                      <p className="text-sm text-gray-500 mt-1">{project.description}</p>
                    )}
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-gray-400">
                        {new Date(project.created_at).toLocaleDateString()}
                      </span>
                      {project.members && (
                        <span className="text-xs text-gray-500">
                          {project.members.length} member{project.members.length !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
                <div className="pt-2">
                  <Link to="/projects">
                    <Button variant="outline" className="w-full">
                      View All Projects
                    </Button>
                  </Link>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No projects yet</h3>
                <p className="mt-1 text-sm text-gray-500">Start collaborating by creating a project.</p>
                <div className="mt-6">
                  <Link to="/projects">
                    <Button>Create Project</Button>
                  </Link>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
