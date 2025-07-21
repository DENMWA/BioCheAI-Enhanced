import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { dataSourceApi } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { toast } from 'sonner';
import {
  Layers,
  Plus,
  Database,
  FileText,
  Image,
  Activity,
  Link,
  Loader2,
  BarChart3,
} from 'lucide-react';

const DataIntegration: React.FC = () => {
  const [isRegisterDialogOpen, setIsRegisterDialogOpen] = useState(false);
  const [newDataSource, setNewDataSource] = useState({
    name: '',
    source_type: '',
    source_format: '',
    file_path: '',
    url: '',
    description: '',
  });
  const [integrationConfig, setIntegrationConfig] = useState({
    name: '',
    description: '',
    source_ids: [] as number[],
  });
  const queryClient = useQueryClient();

  const registerSourceMutation = useMutation({
    mutationFn: dataSourceApi.register,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['data-sources'] });
      toast.success('Your data source is now available for integration');
      setNewDataSource({
        name: '',
        source_type: '',
        source_format: '',
        file_path: '',
        url: '',
        description: '',
      });
      setIsRegisterDialogOpen(false);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to register data source');
    },
  });

  const createIntegrationMutation = useMutation({
    mutationFn: dataSourceApi.createIntegration,
    onSuccess: () => {
      toast.success('Multi-modal data integration is now processing');
      setIntegrationConfig({
        name: '',
        description: '',
        source_ids: [],
      });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create integration');
    },
  });

  const handleRegisterSource = () => {
    if (!newDataSource.name.trim() || !newDataSource.source_type) {
      toast.error('Please provide name and source type');
      return;
    }

    registerSourceMutation.mutate({
      ...newDataSource,
      source_metadata: {
        description: newDataSource.description,
      },
    });
  };

  const handleCreateIntegration = () => {
    if (!integrationConfig.name.trim() || integrationConfig.source_ids.length < 2) {
      toast.error('Please provide a name and select at least 2 data sources');
      return;
    }

    createIntegrationMutation.mutate(integrationConfig);
  };

  const getSourceTypeIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'omics':
        return <Activity className="h-5 w-5" />;
      case 'clinical':
        return <FileText className="h-5 w-5" />;
      case 'imaging':
        return <Image className="h-5 w-5" />;
      case 'literature':
        return <FileText className="h-5 w-5" />;
      default:
        return <Database className="h-5 w-5" />;
    }
  };

  const getSourceTypeColor = (sourceType: string) => {
    switch (sourceType) {
      case 'omics':
        return 'bg-blue-500';
      case 'clinical':
        return 'bg-green-500';
      case 'imaging':
        return 'bg-purple-500';
      case 'literature':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const mockDataSources = [
    {
      id: 1,
      name: 'RNA-seq Dataset',
      source_type: 'omics',
      source_format: 'FASTQ',
      quality_score: 0.95,
      records: 50000,
    },
    {
      id: 2,
      name: 'Clinical Trial Data',
      source_type: 'clinical',
      source_format: 'CSV',
      quality_score: 0.88,
      records: 1200,
    },
    {
      id: 3,
      name: 'MRI Scans',
      source_type: 'imaging',
      source_format: 'DICOM',
      quality_score: 0.92,
      records: 800,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Multi-Modal Data Integration</h1>
          <p className="text-gray-600 mt-1">
            Integrate and harmonize diverse data types for comprehensive analysis
          </p>
        </div>
        <Dialog open={isRegisterDialogOpen} onOpenChange={setIsRegisterDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Register Data Source
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Register New Data Source</DialogTitle>
              <DialogDescription>
                Add a new data source for multi-modal integration
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="source-name">Data Source Name</Label>
                  <Input
                    id="source-name"
                    placeholder="e.g., RNA-seq Dataset"
                    value={newDataSource.name}
                    onChange={(e) => setNewDataSource({ ...newDataSource, name: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="source-type">Source Type</Label>
                  <Select
                    value={newDataSource.source_type}
                    onValueChange={(value) => setNewDataSource({ ...newDataSource, source_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="omics">Omics Data</SelectItem>
                      <SelectItem value="clinical">Clinical Data</SelectItem>
                      <SelectItem value="imaging">Imaging Data</SelectItem>
                      <SelectItem value="literature">Literature Data</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="source-format">Data Format</Label>
                  <Input
                    id="source-format"
                    placeholder="e.g., FASTQ, CSV, DICOM"
                    value={newDataSource.source_format}
                    onChange={(e) => setNewDataSource({ ...newDataSource, source_format: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="source-url">URL (Optional)</Label>
                  <Input
                    id="source-url"
                    placeholder="https://..."
                    value={newDataSource.url}
                    onChange={(e) => setNewDataSource({ ...newDataSource, url: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="file-path">File Path (Optional)</Label>
                <Input
                  id="file-path"
                  placeholder="/path/to/data/file"
                  value={newDataSource.file_path}
                  onChange={(e) => setNewDataSource({ ...newDataSource, file_path: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="source-description">Description</Label>
                <Textarea
                  id="source-description"
                  placeholder="Describe your data source..."
                  value={newDataSource.description}
                  onChange={(e) => setNewDataSource({ ...newDataSource, description: e.target.value })}
                />
              </div>

              <Button
                onClick={handleRegisterSource}
                disabled={registerSourceMutation.isPending}
                className="w-full"
              >
                {registerSourceMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Registering Source...
                  </>
                ) : (
                  'Register Data Source'
                )}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs defaultValue="sources" className="space-y-6">
        <TabsList>
          <TabsTrigger value="sources">Data Sources</TabsTrigger>
          <TabsTrigger value="integration">Multi-Modal Integration</TabsTrigger>
        </TabsList>

        <TabsContent value="sources" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockDataSources.map((source) => (
              <Card key={source.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getSourceTypeColor(source.source_type)}`}>
                        {getSourceTypeIcon(source.source_type)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{source.name}</CardTitle>
                        <CardDescription>{source.source_type}</CardDescription>
                      </div>
                    </div>
                    <Badge variant="outline">{source.source_format}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Quality Score</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${source.quality_score * 100}%` }}
                          ></div>
                        </div>
                        <span className="font-medium">{Math.round(source.quality_score * 100)}%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Records</span>
                      <span className="font-medium">{source.records.toLocaleString()}</span>
                    </div>
                    <div className="pt-2">
                      <Button size="sm" variant="outline" className="w-full">
                        <Link className="mr-1 h-4 w-4" />
                        View Schema
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="integration" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Layers className="h-5 w-5" />
                <span>Create Multi-Modal Integration</span>
              </CardTitle>
              <CardDescription>
                Combine multiple data sources for comprehensive analysis
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="integration-name">Integration Name</Label>
                  <Input
                    id="integration-name"
                    placeholder="e.g., Cancer Multi-Omics Study"
                    value={integrationConfig.name}
                    onChange={(e) => setIntegrationConfig({ ...integrationConfig, name: e.target.value })}
                  />
                </div>
                <div>
                  <Label>Selected Sources</Label>
                  <div className="text-sm text-gray-600">
                    {integrationConfig.source_ids.length} sources selected
                  </div>
                </div>
              </div>

              <div>
                <Label htmlFor="integration-description">Description</Label>
                <Textarea
                  id="integration-description"
                  placeholder="Describe your integration objectives..."
                  value={integrationConfig.description}
                  onChange={(e) => setIntegrationConfig({ ...integrationConfig, description: e.target.value })}
                />
              </div>

              <div>
                <Label>Available Data Sources</Label>
                <div className="mt-2 space-y-2 max-h-48 overflow-y-auto">
                  {mockDataSources.map((source) => (
                    <div
                      key={source.id}
                      className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                        integrationConfig.source_ids.includes(source.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => {
                        setIntegrationConfig(prev => ({
                          ...prev,
                          source_ids: prev.source_ids.includes(source.id)
                            ? prev.source_ids.filter(id => id !== source.id)
                            : [...prev.source_ids, source.id]
                        }));
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`p-1 rounded ${getSourceTypeColor(source.source_type)}`}>
                            {getSourceTypeIcon(source.source_type)}
                          </div>
                          <div>
                            <h4 className="font-medium text-sm">{source.name}</h4>
                            <p className="text-xs text-gray-500">{source.source_type} • {source.records.toLocaleString()} records</p>
                          </div>
                        </div>
                        <input
                          type="checkbox"
                          checked={integrationConfig.source_ids.includes(source.id)}
                          onChange={() => {}}
                          className="h-4 w-4 text-blue-600"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <Button
                onClick={handleCreateIntegration}
                disabled={createIntegrationMutation.isPending}
                className="w-full"
              >
                {createIntegrationMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating Integration...
                  </>
                ) : (
                  <>
                    <Layers className="mr-2 h-4 w-4" />
                    Create Integration
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Integration Analytics</span>
              </CardTitle>
              <CardDescription>
                Cross-modal correlation analysis and quality metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No integrations yet</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Create a multi-modal integration to see analytics and correlations
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DataIntegration;
