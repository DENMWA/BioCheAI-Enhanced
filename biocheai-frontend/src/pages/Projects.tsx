import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { projectApi, collaborationApi } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { websocketService } from '../lib/websocket';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Switch } from '../components/ui/switch';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import {
  Users,
  Plus,
  Settings,
  Share2,
  MessageSquare,
  Activity,
  Globe,
  Lock,
  Loader2,
  Calendar,
} from 'lucide-react';

const Projects: React.FC = () => {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    is_public: false,
  });
  const { user } = useAuth();
  const queryClient = useQueryClient();

  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectApi.getAll,
  });

  const createProjectMutation = useMutation({
    mutationFn: projectApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Your new research project is ready for collaboration');
      setNewProject({ name: '', description: '', is_public: false });
      setIsCreateDialogOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create project');
    },
  });

  const createSessionMutation = useMutation({
    mutationFn: collaborationApi.createSession,
    onSuccess: (data) => {
      if (user) {
        websocketService.joinSession(data.session.id, user.id);
      }
      toast.success('You can now collaborate in real-time');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to start collaboration session');
    },
  });

  const handleCreateProject = () => {
    if (!newProject.name.trim()) {
      toast.error('Please provide a project name');
      return;
    }

    createProjectMutation.mutate(newProject);
  };

  const handleStartCollaboration = (projectId: number) => {
    createSessionMutation.mutate(projectId);
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner':
        return 'bg-purple-100 text-purple-800';
      case 'admin':
        return 'bg-blue-100 text-blue-800';
      case 'member':
        return 'bg-green-100 text-green-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Projects & Collaboration</h1>
          <p className="text-gray-600 mt-1">
            Manage your research projects and collaborate with team members
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
              <DialogDescription>
                Start a new research project and invite collaborators
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="project-name">Project Name</Label>
                <Input
                  id="project-name"
                  placeholder="e.g., Cancer Genomics Study"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="project-description">Description</Label>
                <Textarea
                  id="project-description"
                  placeholder="Describe your research project..."
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  id="is-public"
                  checked={newProject.is_public}
                  onCheckedChange={(checked) => setNewProject({ ...newProject, is_public: checked })}
                />
                <Label htmlFor="is-public">Make project public</Label>
              </div>
              <Button
                onClick={handleCreateProject}
                disabled={createProjectMutation.isPending}
                className="w-full"
              >
                {createProjectMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Project...
                  </>
                ) : (
                  'Create Project'
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                  <div className="flex items-center space-x-2">
                    {project.is_public ? (
                      <Globe className="h-4 w-4 text-green-500" />
                    ) : (
                      <Lock className="h-4 w-4 text-gray-500" />
                    )}
                    <Badge variant={project.is_public ? "default" : "secondary"}>
                      {project.is_public ? "Public" : "Private"}
                    </Badge>
                  </div>
                </div>
                <CardDescription>
                  {project.description || "No description provided"}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>{new Date(project.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4" />
                      <span>{project.members?.length || 1} member{(project.members?.length || 1) !== 1 ? 's' : ''}</span>
                    </div>
                  </div>

                  {project.members && project.members.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium">Team Members</h4>
                      <div className="flex flex-wrap gap-1">
                        {project.members.slice(0, 3).map((member) => (
                          <Badge
                            key={member.id}
                            variant="outline"
                            className={getRoleColor(member.role)}
                          >
                            {member.role}
                          </Badge>
                        ))}
                        {project.members.length > 3 && (
                          <Badge variant="outline">
                            +{project.members.length - 3} more
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      onClick={() => handleStartCollaboration(project.id)}
                      disabled={createSessionMutation.isPending}
                      className="flex-1"
                    >
                      {createSessionMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Activity className="mr-1 h-4 w-4" />
                          Collaborate
                        </>
                      )}
                    </Button>
                    <Button size="sm" variant="outline">
                      <Settings className="h-4 w-4" />
                    </Button>
                    <Button size="sm" variant="outline">
                      <Share2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No projects yet</h3>
            <p className="mt-2 text-gray-500">
              Create your first research project to start collaborating with your team.
            </p>
            <Button
              className="mt-6"
              onClick={() => setIsCreateDialogOpen(true)}
            >
              <Plus className="mr-2 h-4 w-4" />
              Create Your First Project
            </Button>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MessageSquare className="h-5 w-5" />
            <span>Real-time Collaboration</span>
          </CardTitle>
          <CardDescription>
            Active collaboration sessions and team communications
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Activity className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No active sessions</h3>
            <p className="mt-1 text-sm text-gray-500">
              Start a collaboration session to work with your team in real-time
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Projects;
