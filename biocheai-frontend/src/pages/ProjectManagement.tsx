import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { taskApi, milestoneApi, timelineApi } from '../lib/api';
import GanttChart from '../components/GanttChart';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import {
  Plus,
  Clock,
  Target,
  BarChart3,
  Loader2,
} from 'lucide-react';

const ProjectManagement: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const [isCreateTaskDialogOpen, setIsCreateTaskDialogOpen] = useState(false);
  const [isCreateMilestoneDialogOpen, setIsCreateMilestoneDialogOpen] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    start_date: '',
    end_date: '',
    priority: 'medium',
    estimated_hours: 0,
  });
  const [newMilestone, setNewMilestone] = useState({
    title: '',
    description: '',
    due_date: '',
  });
  const queryClient = useQueryClient();

  const { data: timelineData, isLoading: timelineLoading } = useQuery({
    queryKey: ['timeline', projectId],
    queryFn: () => timelineApi.getProjectTimeline(projectId!),
    enabled: !!projectId,
  });

  const { data: tasks = [], isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks', projectId],
    queryFn: () => taskApi.getAll(projectId!),
    enabled: !!projectId,
  });

  const createTaskMutation = useMutation({
    mutationFn: (taskData: any) => taskApi.create(projectId!, taskData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timeline', projectId] });
      queryClient.invalidateQueries({ queryKey: ['tasks', projectId] });
      toast.success('Task created successfully');
      setNewTask({
        title: '',
        description: '',
        start_date: '',
        end_date: '',
        priority: 'medium',
        estimated_hours: 0,
      });
      setIsCreateTaskDialogOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create task');
    },
  });

  const createMilestoneMutation = useMutation({
    mutationFn: (milestoneData: any) => milestoneApi.create(projectId!, milestoneData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['timeline', projectId] });
      toast.success('Milestone created successfully');
      setNewMilestone({
        title: '',
        description: '',
        due_date: '',
      });
      setIsCreateMilestoneDialogOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create milestone');
    },
  });

  const handleCreateTask = () => {
    if (!newTask.title || !newTask.start_date || !newTask.end_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    createTaskMutation.mutate(newTask);
  };

  const handleCreateMilestone = () => {
    if (!newMilestone.title || !newMilestone.due_date) {
      toast.error('Please fill in all required fields');
      return;
    }

    createMilestoneMutation.mutate(newMilestone);
  };

  const handleTaskClick = (task: any) => {
    toast.info(`Task: ${task.title} - ${task.status}`);
  };

  const handleTaskUpdate = () => {
    toast.info('Task dates updated');
  };

  if (timelineLoading || tasksLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Project Management</h1>
          <p className="text-gray-600 mt-1">
            Gantt charts, timeline visualization, and resource management
          </p>
        </div>
        <div className="flex space-x-2">
          <Dialog open={isCreateTaskDialogOpen} onOpenChange={setIsCreateTaskDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Task
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Task</DialogTitle>
                <DialogDescription>
                  Add a new task to the project timeline
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="task-title">Task Title</Label>
                  <Input
                    id="task-title"
                    placeholder="e.g., Data Analysis Phase"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="task-description">Description</Label>
                  <Textarea
                    id="task-description"
                    placeholder="Describe the task..."
                    value={newTask.description}
                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="start-date">Start Date</Label>
                    <Input
                      id="start-date"
                      type="datetime-local"
                      value={newTask.start_date}
                      onChange={(e) => setNewTask({ ...newTask, start_date: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="end-date">End Date</Label>
                    <Input
                      id="end-date"
                      type="datetime-local"
                      value={newTask.end_date}
                      onChange={(e) => setNewTask({ ...newTask, end_date: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="priority">Priority</Label>
                    <Select value={newTask.priority} onValueChange={(value) => setNewTask({ ...newTask, priority: value })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="estimated-hours">Estimated Hours</Label>
                    <Input
                      id="estimated-hours"
                      type="number"
                      value={newTask.estimated_hours}
                      onChange={(e) => setNewTask({ ...newTask, estimated_hours: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>
                <Button
                  onClick={handleCreateTask}
                  disabled={createTaskMutation.isPending}
                  className="w-full"
                >
                  {createTaskMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating Task...
                    </>
                  ) : (
                    'Create Task'
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={isCreateMilestoneDialogOpen} onOpenChange={setIsCreateMilestoneDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <Target className="mr-2 h-4 w-4" />
                New Milestone
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Milestone</DialogTitle>
                <DialogDescription>
                  Add a milestone to track project progress
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="milestone-title">Milestone Title</Label>
                  <Input
                    id="milestone-title"
                    placeholder="e.g., Phase 1 Complete"
                    value={newMilestone.title}
                    onChange={(e) => setNewMilestone({ ...newMilestone, title: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="milestone-description">Description</Label>
                  <Textarea
                    id="milestone-description"
                    placeholder="Describe the milestone..."
                    value={newMilestone.description}
                    onChange={(e) => setNewMilestone({ ...newMilestone, description: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="due-date">Due Date</Label>
                  <Input
                    id="due-date"
                    type="datetime-local"
                    value={newMilestone.due_date}
                    onChange={(e) => setNewMilestone({ ...newMilestone, due_date: e.target.value })}
                  />
                </div>
                <Button
                  onClick={handleCreateMilestone}
                  disabled={createMilestoneMutation.isPending}
                  className="w-full"
                >
                  {createMilestoneMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating Milestone...
                    </>
                  ) : (
                    'Create Milestone'
                  )}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Project Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tasks</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tasks.length}</div>
            <p className="text-xs text-muted-foreground">
              {tasks.filter(t => t.status === 'completed').length} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.filter(t => t.status === 'in_progress').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Active tasks
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Milestones</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {timelineData?.milestones.length || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Project milestones
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Progress</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {tasks.length > 0 ? Math.round(
                tasks.reduce((sum, task) => sum + task.progress_percentage, 0) / tasks.length
              ) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              Overall completion
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gantt Chart and Timeline */}
      {timelineData && (
        <GanttChart
          timelineData={timelineData}
          onTaskClick={handleTaskClick}
          onTaskUpdate={handleTaskUpdate}
        />
      )}
    </div>
  );
};

export default ProjectManagement;
