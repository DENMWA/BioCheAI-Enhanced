import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dataApi, analysisApi } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import {
  Database,
  Download,
  Play,
  CheckCircle,
  AlertCircle,
  Activity,
  Search,
  FileText,
  Dna,
  Loader2,
} from 'lucide-react';

const DataFetching: React.FC = () => {
  const [selectedRepository, setSelectedRepository] = useState('');
  const [fetchParams, setFetchParams] = useState<Record<string, any>>({});
  const [analysisData, setAnalysisData] = useState({
    title: '',
    description: '',
    analysis_type: 'protein',
  });
  const queryClient = useQueryClient();

  const { data: repositories = [], isLoading: repositoriesLoading } = useQuery({
    queryKey: ['repositories'],
    queryFn: dataApi.getRepositories,
  });

  const { data: analyses = [], isLoading: analysesLoading } = useQuery({
    queryKey: ['analyses'],
    queryFn: analysisApi.getAll,
  });

  const fetchDataMutation = useMutation({
    mutationFn: ({ repository, params }: { repository: string; params: any }) =>
      dataApi.fetch(repository, params),
    onSuccess: (data) => {
      toast.success(`Retrieved ${data.count || 'multiple'} records from ${selectedRepository}`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to fetch data');
    },
  });

  const createAnalysisMutation = useMutation({
    mutationFn: analysisApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analyses'] });
      toast.success('Your analysis has been queued for processing');
      setAnalysisData({ title: '', description: '', analysis_type: 'protein' });
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to create analysis');
    },
  });

  const repairAnalysisMutation = useMutation({
    mutationFn: analysisApi.repair,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analyses'] });
      toast.success('Data quality issues have been automatically fixed');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to repair analysis');
    },
  });

  const handleFetchData = () => {
    if (!selectedRepository) {
      toast.error('Please select a data repository');
      return;
    }

    fetchDataMutation.mutate({
      repository: selectedRepository,
      params: fetchParams,
    });
  };

  const handleCreateAnalysis = () => {
    if (!analysisData.title) {
      toast.error('Please provide an analysis title');
      return;
    }

    createAnalysisMutation.mutate({
      ...analysisData,
      data: fetchDataMutation.data || {},
    });
  };

  const getRepositoryIcon = (name: string) => {
    switch (name.toLowerCase()) {
      case 'ncbi':
        return <Dna className="h-5 w-5" />;
      case 'pubmed':
        return <FileText className="h-5 w-5" />;
      default:
        return <Database className="h-5 w-5" />;
    }
  };

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

  const renderRepositoryForm = () => {
    const repo = repositories.find(r => r.name === selectedRepository);
    if (!repo) return null;

    switch (selectedRepository) {
      case 'ncbi':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="term">Search Term</Label>
              <Input
                id="term"
                placeholder="e.g., insulin human"
                value={fetchParams.term || ''}
                onChange={(e) => setFetchParams({ ...fetchParams, term: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="db">Database</Label>
              <Select
                value={fetchParams.db || ''}
                onValueChange={(value) => setFetchParams({ ...fetchParams, db: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select database" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="protein">Protein</SelectItem>
                  <SelectItem value="nucleotide">Nucleotide</SelectItem>
                  <SelectItem value="pubmed">PubMed</SelectItem>
                  <SelectItem value="gene">Gene</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="retmax">Max Results</Label>
              <Input
                id="retmax"
                type="number"
                placeholder="10"
                value={fetchParams.retmax || ''}
                onChange={(e) => setFetchParams({ ...fetchParams, retmax: parseInt(e.target.value) })}
              />
            </div>
          </div>
        );
      case 'pubmed':
        return (
          <div className="space-y-4">
            <div>
              <Label htmlFor="query">Search Query</Label>
              <Input
                id="query"
                placeholder="e.g., CRISPR gene editing"
                value={fetchParams.query || ''}
                onChange={(e) => setFetchParams({ ...fetchParams, query: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="max_results">Max Results</Label>
              <Input
                id="max_results"
                type="number"
                placeholder="20"
                value={fetchParams.max_results || ''}
                onChange={(e) => setFetchParams({ ...fetchParams, max_results: parseInt(e.target.value) })}
              />
            </div>
          </div>
        );
      default:
        return (
          <div>
            <Label htmlFor="query">Query</Label>
            <Input
              id="query"
              placeholder="Enter search query"
              value={fetchParams.query || ''}
              onChange={(e) => setFetchParams({ ...fetchParams, query: e.target.value })}
            />
          </div>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Data Fetching & Analysis</h1>
        <p className="text-gray-600 mt-1">
          Fetch data from external repositories and create AI-powered analyses
        </p>
      </div>

      <Tabs defaultValue="fetch" className="space-y-6">
        <TabsList>
          <TabsTrigger value="fetch">Data Fetching</TabsTrigger>
          <TabsTrigger value="analyses">My Analyses</TabsTrigger>
        </TabsList>

        <TabsContent value="fetch" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Database className="h-5 w-5" />
                  <span>Select Data Repository</span>
                </CardTitle>
                <CardDescription>
                  Choose from supported biological databases
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {repositoriesLoading ? (
                  <div className="space-y-3">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="animate-pulse">
                        <div className="h-12 bg-gray-200 rounded"></div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-3">
                    {repositories.map((repo) => (
                      <div
                        key={repo.name}
                        className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                          selectedRepository === repo.name
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedRepository(repo.name)}
                      >
                        <div className="flex items-center space-x-3">
                          {getRepositoryIcon(repo.name)}
                          <div className="flex-1">
                            <h4 className="font-medium">{repo.name.toUpperCase()}</h4>
                            <p className="text-sm text-gray-500">{repo.description}</p>
                          </div>
                          <div className="text-right">
                            <Badge variant="outline">{repo.rate_limit}</Badge>
                          </div>
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
                  <Search className="h-5 w-5" />
                  <span>Search Parameters</span>
                </CardTitle>
                <CardDescription>
                  Configure your data search query
                </CardDescription>
              </CardHeader>
              <CardContent>
                {selectedRepository ? (
                  <div className="space-y-4">
                    {renderRepositoryForm()}
                    <Button
                      onClick={handleFetchData}
                      disabled={fetchDataMutation.isPending}
                      className="w-full"
                    >
                      {fetchDataMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Fetching Data...
                        </>
                      ) : (
                        <>
                          <Download className="mr-2 h-4 w-4" />
                          Fetch Data
                        </>
                      )}
                    </Button>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Database className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="text-gray-500 mt-2">Select a repository to configure search parameters</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {fetchDataMutation.data && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span>Fetched Data</span>
                </CardTitle>
                <CardDescription>
                  Data successfully retrieved from {selectedRepository}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      Retrieved {fetchDataMutation.data.count || 'multiple'} records. 
                      Create an analysis to process this data with AI policing and auto-repair.
                    </AlertDescription>
                  </Alert>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="analysis-title">Analysis Title</Label>
                      <Input
                        id="analysis-title"
                        placeholder="e.g., Insulin Protein Analysis"
                        value={analysisData.title}
                        onChange={(e) => setAnalysisData({ ...analysisData, title: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="analysis-type">Analysis Type</Label>
                      <Select
                        value={analysisData.analysis_type}
                        onValueChange={(value) => setAnalysisData({ ...analysisData, analysis_type: value })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="protein">Protein Analysis</SelectItem>
                          <SelectItem value="dna">DNA Analysis</SelectItem>
                          <SelectItem value="rna">RNA Analysis</SelectItem>
                          <SelectItem value="multiomics">Multi-omics</SelectItem>
                          <SelectItem value="literature">Literature Review</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="analysis-description">Description (Optional)</Label>
                    <Textarea
                      id="analysis-description"
                      placeholder="Describe your analysis objectives..."
                      value={analysisData.description}
                      onChange={(e) => setAnalysisData({ ...analysisData, description: e.target.value })}
                    />
                  </div>

                  <Button
                    onClick={handleCreateAnalysis}
                    disabled={createAnalysisMutation.isPending}
                    className="w-full"
                  >
                    {createAnalysisMutation.isPending ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creating Analysis...
                      </>
                    ) : (
                      <>
                        <Play className="mr-2 h-4 w-4" />
                        Create Analysis with AI Policing
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="analyses" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>My Analyses</CardTitle>
              <CardDescription>
                Track your analysis progress and results
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysesLoading ? (
                <div className="space-y-3">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-16 bg-gray-200 rounded"></div>
                    </div>
                  ))}
                </div>
              ) : analyses.length > 0 ? (
                <div className="space-y-4">
                  {analyses.map((analysis) => (
                    <div key={analysis.id} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(analysis.status)}
                          <div>
                            <h4 className="font-medium">{analysis.title}</h4>
                            <p className="text-sm text-gray-500">{analysis.analysis_type}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={getStatusBadge(analysis.status)}>
                            {analysis.status}
                          </Badge>
                          {analysis.compliance_score && (
                            <span className="text-sm text-gray-500">
                              {Math.round(analysis.compliance_score * 100)}% compliant
                            </span>
                          )}
                          {analysis.status === 'failed' && (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => repairAnalysisMutation.mutate(analysis.id)}
                              disabled={repairAnalysisMutation.isPending}
                            >
                              {repairAnalysisMutation.isPending ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                'Repair'
                              )}
                            </Button>
                          )}
                        </div>
                      </div>
                      {analysis.progress > 0 && analysis.status === 'running' && (
                        <div className="mt-2">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${analysis.progress}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{analysis.progress}% complete</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Database className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No analyses yet</h3>
                  <p className="mt-1 text-sm text-gray-500">Create your first analysis by fetching data.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DataFetching;
