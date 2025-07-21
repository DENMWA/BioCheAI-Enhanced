import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { cloudApi } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import {
  Cloud,
  Server,
  Upload,
  Activity,
  BarChart3,
  Settings,
  Zap,
  Database,
  Loader2,
  TrendingUp,
} from 'lucide-react';

const CloudScaling: React.FC = () => {
  const [scaleConfig, setScaleConfig] = useState({
    analysisId: '',
    targetInstances: 1,
    provider: 'aws',
  });
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  const { data: cloudStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['cloud-status'],
    queryFn: cloudApi.getStatus,
  });

  const scaleMutation = useMutation({
    mutationFn: ({ analysisId, targetInstances }: { analysisId: number; targetInstances: number }) =>
      cloudApi.scale(analysisId, targetInstances),
    onSuccess: () => {
      toast.success('Analysis scaling initiated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to scale analysis');
    },
  });

  const uploadMutation = useMutation({
    mutationFn: ({ file, provider }: { file: File; provider: string }) =>
      cloudApi.uploadToCloud(file, provider),
    onSuccess: () => {
      toast.success('File uploaded to cloud storage successfully');
      setUploadFile(null);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to upload file');
    },
  });

  const handleScale = () => {
    if (!scaleConfig.analysisId) {
      toast.error('Please provide an analysis ID');
      return;
    }

    scaleMutation.mutate({
      analysisId: parseInt(scaleConfig.analysisId),
      targetInstances: scaleConfig.targetInstances,
    });
  };

  const handleUpload = () => {
    if (!uploadFile) {
      toast.error('Please select a file to upload');
      return;
    }

    uploadMutation.mutate({
      file: uploadFile,
      provider: scaleConfig.provider,
    });
  };

  const getProviderIcon = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'aws':
        return <Cloud className="h-5 w-5" />;
      case 'gcp':
        return <Cloud className="h-5 w-5" />;
      case 'azure':
        return <Cloud className="h-5 w-5" />;
      default:
        return <Server className="h-5 w-5" />;
    }
  };

  const getProviderColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'aws':
        return 'bg-orange-500';
      case 'gcp':
        return 'bg-blue-500';
      case 'azure':
        return 'bg-blue-600';
      default:
        return 'bg-gray-500';
    }
  };

  const mockCloudProviders = [
    {
      name: 'AWS',
      value: 'aws',
      status: 'active',
      instances: 3,
      cost: 45.67,
    },
    {
      name: 'Google Cloud',
      value: 'gcp',
      status: 'active',
      instances: 1,
      cost: 12.34,
    },
    {
      name: 'Azure',
      value: 'azure',
      status: 'inactive',
      instances: 0,
      cost: 0,
    },
  ];

  const mockMetrics = {
    totalInstances: 4,
    totalCost: 58.01,
    cpuUtilization: 67,
    memoryUtilization: 54,
    storageUsed: 1.2,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Cloud Scaling & Management</h1>
        <p className="text-gray-600 mt-1">
          Scale your analyses across cloud providers and manage resources
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Instances</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockMetrics.totalInstances}</div>
            <p className="text-xs text-muted-foreground">Across all providers</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Cost</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${mockMetrics.totalCost}</div>
            <p className="text-xs text-muted-foreground">Current month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">CPU Usage</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockMetrics.cpuUtilization}%</div>
            <p className="text-xs text-muted-foreground">Average utilization</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Memory Usage</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockMetrics.memoryUtilization}%</div>
            <p className="text-xs text-muted-foreground">Average utilization</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Storage</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockMetrics.storageUsed} TB</div>
            <p className="text-xs text-muted-foreground">Total used</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="providers" className="space-y-6">
        <TabsList>
          <TabsTrigger value="providers">Cloud Providers</TabsTrigger>
          <TabsTrigger value="scaling">Auto Scaling</TabsTrigger>
          <TabsTrigger value="storage">Cloud Storage</TabsTrigger>
        </TabsList>

        <TabsContent value="providers" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {mockCloudProviders.map((provider) => (
              <Card key={provider.value} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getProviderColor(provider.value)}`}>
                        {getProviderIcon(provider.value)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{provider.name}</CardTitle>
                        <CardDescription>
                          {provider.instances} instance{provider.instances !== 1 ? 's' : ''}
                        </CardDescription>
                      </div>
                    </div>
                    <Badge variant={provider.status === 'active' ? 'default' : 'secondary'}>
                      {provider.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Monthly Cost</span>
                      <span className="font-medium">${provider.cost}</span>
                    </div>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline" className="flex-1">
                        <Settings className="mr-1 h-4 w-4" />
                        Configure
                      </Button>
                      <Button size="sm" variant="outline" className="flex-1">
                        <BarChart3 className="mr-1 h-4 w-4" />
                        Metrics
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="scaling" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="h-5 w-5" />
                <span>Scale Analysis</span>
              </CardTitle>
              <CardDescription>
                Scale your analyses across multiple cloud instances
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="analysis-id">Analysis ID</Label>
                  <Input
                    id="analysis-id"
                    placeholder="Enter analysis ID"
                    value={scaleConfig.analysisId}
                    onChange={(e) => setScaleConfig({ ...scaleConfig, analysisId: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="target-instances">Target Instances</Label>
                  <Input
                    id="target-instances"
                    type="number"
                    min="1"
                    max="10"
                    value={scaleConfig.targetInstances}
                    onChange={(e) => setScaleConfig({ ...scaleConfig, targetInstances: parseInt(e.target.value) || 1 })}
                  />
                </div>
                <div>
                  <Label htmlFor="provider-select">Cloud Provider</Label>
                  <Select
                    value={scaleConfig.provider}
                    onValueChange={(value) => setScaleConfig({ ...scaleConfig, provider: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="aws">AWS</SelectItem>
                      <SelectItem value="gcp">Google Cloud</SelectItem>
                      <SelectItem value="azure">Azure</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button
                onClick={handleScale}
                disabled={scaleMutation.isPending}
                className="w-full"
              >
                {scaleMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Scaling Analysis...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-4 w-4" />
                    Scale Analysis
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="storage" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="h-5 w-5" />
                <span>Cloud Storage</span>
              </CardTitle>
              <CardDescription>
                Upload and manage files in cloud storage
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="file-upload">Select File</Label>
                <Input
                  id="file-upload"
                  type="file"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                />
              </div>

              <div>
                <Label htmlFor="storage-provider">Storage Provider</Label>
                <Select
                  value={scaleConfig.provider}
                  onValueChange={(value) => setScaleConfig({ ...scaleConfig, provider: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="aws">AWS S3</SelectItem>
                    <SelectItem value="gcp">Google Cloud Storage</SelectItem>
                    <SelectItem value="azure">Azure Blob Storage</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button
                onClick={handleUpload}
                disabled={uploadMutation.isPending || !uploadFile}
                className="w-full"
              >
                {uploadMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading File...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload to Cloud
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CloudScaling;
