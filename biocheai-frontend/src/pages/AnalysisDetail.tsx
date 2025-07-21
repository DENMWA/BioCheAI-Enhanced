import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { analysisApi } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import {
  CheckCircle,
  AlertCircle,
  Activity,
  BarChart3,
  FileText,
  Download,
  RefreshCw,
} from 'lucide-react';

const AnalysisDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  const { data: analysis, isLoading } = useQuery({
    queryKey: ['analysis', id],
    queryFn: () => analysisApi.getById(parseInt(id!)),
    enabled: !!id,
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'running':
        return <Activity className="h-5 w-5 text-blue-500 animate-pulse" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
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

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-20 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-12">
        <AlertCircle className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-4 text-lg font-medium text-gray-900">Analysis not found</h3>
        <p className="mt-2 text-gray-500">The requested analysis could not be found.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{analysis.title}</h1>
          <p className="text-gray-600 mt-1">
            {analysis.description || `${analysis.analysis_type} analysis`}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {getStatusIcon(analysis.status)}
          <Badge variant={getStatusBadge(analysis.status)}>
            {analysis.status}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Status</CardTitle>
            {getStatusIcon(analysis.status)}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">{analysis.status}</div>
            <p className="text-xs text-muted-foreground">
              {analysis.status === 'running' && `${analysis.progress}% complete`}
              {analysis.status === 'completed' && 'Analysis finished'}
              {analysis.status === 'failed' && 'Requires attention'}
              {analysis.status === 'pending' && 'Waiting to start'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analysis.compliance_score ? Math.round(analysis.compliance_score * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              AI policing assessment
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Confidence</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {analysis.confidence_score ? Math.round(analysis.confidence_score * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              ML prediction confidence
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Created</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Date(analysis.created_at).toLocaleDateString()}
            </div>
            <p className="text-xs text-muted-foreground">
              {new Date(analysis.created_at).toLocaleTimeString()}
            </p>
          </CardContent>
        </Card>
      </div>

      {analysis.status === 'running' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Analysis Progress</span>
            </CardTitle>
            <CardDescription>
              Current processing status and progress
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Progress</span>
                <span className="text-sm text-gray-500">{analysis.progress}%</span>
              </div>
              <Progress value={analysis.progress} className="w-full" />
              <div className="text-sm text-gray-600">
                Analysis is currently running. Results will be available once processing is complete.
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Input Data</CardTitle>
            <CardDescription>
              Data used for this analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Analysis Type</span>
                <Badge variant="outline">{analysis.analysis_type}</Badge>
              </div>
              {analysis.input_data && (
                <div className="text-sm text-gray-600">
                  <pre className="bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                    {JSON.stringify(analysis.input_data, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI Policing Report</CardTitle>
            <CardDescription>
              Automated quality and compliance assessment
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analysis.police_report ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Status</span>
                  <Badge variant={analysis.police_report.status === 'clean' ? 'default' : 'destructive'}>
                    {analysis.police_report.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Compliance Score</span>
                  <span className="text-sm font-bold">
                    {Math.round((analysis.police_report.compliance_score || 0) * 100)}%
                  </span>
                </div>
                {analysis.police_report.violations && analysis.police_report.violations.length > 0 && (
                  <div>
                    <span className="text-sm font-medium">Violations</span>
                    <ul className="mt-1 text-sm text-red-600">
                      {analysis.police_report.violations.map((violation: any, index: number) => (
                        <li key={index}>• {violation.message || violation}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-sm text-gray-500">
                No policing report available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {analysis.results && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Analysis Results</span>
              <Button size="sm" variant="outline">
                <Download className="mr-1 h-4 w-4" />
                Export
              </Button>
            </CardTitle>
            <CardDescription>
              Generated insights and predictions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {analysis.ml_predictions && (
                <div>
                  <h4 className="font-medium mb-2">ML Predictions</h4>
                  <div className="bg-gray-50 p-3 rounded text-sm">
                    <pre className="overflow-x-auto">
                      {JSON.stringify(analysis.ml_predictions, null, 2)}
                    </pre>
                  </div>
                </div>
              )}
              
              <div>
                <h4 className="font-medium mb-2">Full Results</h4>
                <div className="bg-gray-50 p-3 rounded text-sm">
                  <pre className="overflow-x-auto">
                    {JSON.stringify(analysis.results, null, 2)}
                  </pre>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {analysis.error_message && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span>Error Details</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-red-600 bg-red-50 p-3 rounded">
              {analysis.error_message}
            </div>
            <div className="mt-4">
              <Button size="sm" variant="outline">
                <RefreshCw className="mr-1 h-4 w-4" />
                Retry Analysis
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AnalysisDetail;
