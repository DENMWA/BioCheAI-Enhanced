import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { workflowApi } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import {
  Workflow,
  Plus,
  Play,
  Settings,
  ArrowRight,
  Database,
  Filter,
  BarChart3,
  Download,
  Loader2,
  Zap,
} from 'lucide-react';

const Workflows: React.FC = () => {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
  });
  const queryClient = useQueryClient();

  const { data: templates = [], isLoading: templatesLoading } = useQuery({
    queryKey: ['workflow-templates'],
    queryFn: workflowApi.getTemplates,
  });

  const createWorkflowMutation = useMutation({
    mutationFn: workflowApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      toast.success('Your analysis pipeline is ready to execute');
      setNewWorkflow({ name: '', description: '' });
      setSelectedTemplate('');
      setIsCreateDialogOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create workflow');
    },
  });


  const handleCreateWorkflow = () => {
    if (!newWorkflow.name.trim()) {
      toast.error('Please provide a workflow name');
      return;
    }

    if (!selectedTemplate) {
      toast.error('Please select a workflow template');
      return;
    }

    const template = templates.find(t => t.name === selectedTemplate);
    createWorkflowMutation.mutate({
      ...newWorkflow,
      template_type: selectedTemplate,
      steps: template?.steps || [],
    });
  };

  const getStepIcon = (stepType: string) => {
    switch (stepType) {
      case 'data_fetch':
        return <Database className="h-4 w-4" />;
      case 'data_filter':
        return <Filter className="h-4 w-4" />;
      case 'analysis':
        return <BarChart3 className="h-4 w-4" />;
      case 'visualization':
        return <BarChart3 className="h-4 w-4" />;
      case 'export':
        return <Download className="h-4 w-4" />;
      default:
        return <Settings className="h-4 w-4" />;
    }
  };

  const getTemplateColor = (templateType: string) => {
    switch (templateType) {
      case 'genomic_analysis':
        return 'bg-blue-500';
      case 'literature_review':
        return 'bg-green-500';
      case 'multimodal_integration':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">No-Code Workflow Builder</h1>
          <p className="text-gray-600 mt-1">
            Create and execute analysis pipelines without coding
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Workflow
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Workflow</DialogTitle>
              <DialogDescription>
                Choose a template and customize your analysis pipeline
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="workflow-name">Workflow Name</Label>
                  <Input
                    id="workflow-name"
                    placeholder="e.g., Protein Analysis Pipeline"
                    value={newWorkflow.name}
                    onChange={(e) => setNewWorkflow({ ...newWorkflow, name: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="template-select">Template</Label>
                  <Select value={selectedTemplate} onValueChange={setSelectedTemplate}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select template" />
                    </SelectTrigger>
                    <SelectContent>
                      {templates.map((template) => (
                        <SelectItem key={template.name} value={template.name}>
                          {template.display_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="workflow-description">Description</Label>
                <Textarea
                  id="workflow-description"
                  placeholder="Describe your workflow objectives..."
                  value={newWorkflow.description}
                  onChange={(e) => setNewWorkflow({ ...newWorkflow, description: e.target.value })}
                />
              </div>

              {selectedTemplate && (
                <div>
                  <Label>Workflow Steps Preview</Label>
                  <div className="mt-2 p-4 bg-gray-50 rounded-lg">
                    {templates.find(t => t.name === selectedTemplate)?.steps.map((step: any, index: number) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        {getStepIcon(step.type)}
                        <span className="text-sm">{step.name}</span>
                        {index < templates.find(t => t.name === selectedTemplate)!.steps.length - 1 && (
                          <ArrowRight className="h-4 w-4 text-gray-400" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <Button
                onClick={handleCreateWorkflow}
                disabled={createWorkflowMutation.isPending}
                className="w-full"
              >
                {createWorkflowMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Workflow...
                  </>
                ) : (
                  'Create Workflow'
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5" />
              <span>Workflow Templates</span>
            </CardTitle>
            <CardDescription>
              Pre-built analysis pipelines for common research tasks
            </CardDescription>
          </CardHeader>
          <CardContent>
            {templatesLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-16 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {templates.map((template) => (
                  <div key={template.name} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${getTemplateColor(template.name)}`}>
                          <Workflow className="h-4 w-4 text-white" />
                        </div>
                        <div>
                          <h4 className="font-medium">{template.display_name}</h4>
                          <p className="text-sm text-gray-500">{template.description}</p>
                        </div>
                      </div>
                      <Badge variant="outline">{template.steps.length} steps</Badge>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      {template.steps.map((step: any, index: number) => (
                        <React.Fragment key={index}>
                          <span>{step.name}</span>
                          {index < template.steps.length - 1 && (
                            <ArrowRight className="h-3 w-3" />
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Play className="h-5 w-5" />
              <span>Quick Start</span>
            </CardTitle>
            <CardDescription>
              Execute workflows with sample data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center py-8">
                <Workflow className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No workflows yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Create your first workflow to start building analysis pipelines
                </p>
                <Button
                  className="mt-4"
                  onClick={() => setIsCreateDialogOpen(true)}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Create Workflow
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Workflow Execution History</CardTitle>
          <CardDescription>
            Track your workflow runs and results
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No executions yet</h3>
            <p className="mt-1 text-sm text-gray-500">
              Workflow execution history will appear here
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Workflows;
