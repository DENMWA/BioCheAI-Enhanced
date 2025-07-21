import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { complianceApi } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import {
  Shield,
  FileText,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Download,
  Loader2,
  Globe,
  Lock,
  Eye,
} from 'lucide-react';

const Compliance: React.FC = () => {
  const [selectedFramework, setSelectedFramework] = useState('');
  const [analysisId, setAnalysisId] = useState('');

  useQuery({
    queryKey: ['compliance-frameworks'],
    queryFn: complianceApi.getFrameworks,
  });

  const generateReportMutation = useMutation({
    mutationFn: ({ analysisId, framework }: { analysisId: number; framework: string }) =>
      complianceApi.generateReport(analysisId, framework),
    onSuccess: () => {
      toast.success('Compliance report generated successfully');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to generate compliance report');
    },
  });

  const handleGenerateReport = () => {
    if (!analysisId || !selectedFramework) {
      toast.error('Please select an analysis and compliance framework');
      return;
    }

    generateReportMutation.mutate({
      analysisId: parseInt(analysisId),
      framework: selectedFramework,
    });
  };

  const getFrameworkIcon = (framework: string) => {
    switch (framework.toLowerCase()) {
      case 'gdpr':
        return <Globe className="h-5 w-5" />;
      case 'hipaa':
        return <Lock className="h-5 w-5" />;
      case 'fda':
        return <Shield className="h-5 w-5" />;
      case 'ema':
        return <Eye className="h-5 w-5" />;
      default:
        return <Shield className="h-5 w-5" />;
    }
  };

  const getFrameworkColor = (framework: string) => {
    switch (framework.toLowerCase()) {
      case 'gdpr':
        return 'bg-blue-500';
      case 'hipaa':
        return 'bg-green-500';
      case 'fda':
        return 'bg-red-500';
      case 'ema':
        return 'bg-purple-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getComplianceStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'compliant':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'violation':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const mockComplianceReports = [
    {
      id: 1,
      framework: 'GDPR',
      status: 'compliant',
      score: 95,
      violations: 0,
      warnings: 2,
      generated_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 2,
      framework: 'HIPAA',
      status: 'warning',
      score: 78,
      violations: 1,
      warnings: 5,
      generated_at: '2024-01-14T14:20:00Z',
    },
    {
      id: 3,
      framework: 'FDA',
      status: 'compliant',
      score: 88,
      violations: 0,
      warnings: 3,
      generated_at: '2024-01-13T09:15:00Z',
    },
  ];

  const mockFrameworks = ['GDPR', 'HIPAA', 'FDA', 'EMA'];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Regulatory Compliance</h1>
        <p className="text-gray-600 mt-1">
          Ensure your research meets regulatory standards and compliance requirements
        </p>
      </div>

      <Tabs defaultValue="frameworks" className="space-y-6">
        <TabsList>
          <TabsTrigger value="frameworks">Compliance Frameworks</TabsTrigger>
          <TabsTrigger value="reports">Compliance Reports</TabsTrigger>
          <TabsTrigger value="audit">Audit Trail</TabsTrigger>
        </TabsList>

        <TabsContent value="frameworks" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {mockFrameworks.map((framework) => (
              <Card key={framework} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${getFrameworkColor(framework)}`}>
                      {getFrameworkIcon(framework)}
                    </div>
                    <div>
                      <CardTitle className="text-lg">{framework}</CardTitle>
                      <CardDescription>
                        {framework === 'GDPR' && 'European Data Protection'}
                        {framework === 'HIPAA' && 'Healthcare Privacy'}
                        {framework === 'FDA' && 'Medical Device Standards'}
                        {framework === 'EMA' && 'European Medicines'}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600">
                      Automated compliance checking and reporting for {framework} requirements
                    </div>
                    <Button size="sm" variant="outline" className="w-full">
                      <FileText className="mr-1 h-4 w-4" />
                      View Requirements
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Generate Compliance Report</span>
              </CardTitle>
              <CardDescription>
                Create detailed compliance reports for your analyses
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="analysis-id">Analysis ID</Label>
                  <Input
                    id="analysis-id"
                    placeholder="Enter analysis ID"
                    value={analysisId}
                    onChange={(e) => setAnalysisId(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="framework-select">Compliance Framework</Label>
                  <Select value={selectedFramework} onValueChange={setSelectedFramework}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select framework" />
                    </SelectTrigger>
                    <SelectContent>
                      {mockFrameworks.map((framework) => (
                        <SelectItem key={framework} value={framework.toLowerCase()}>
                          {framework}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button
                onClick={handleGenerateReport}
                disabled={generateReportMutation.isPending}
                className="w-full"
              >
                {generateReportMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Generate Compliance Report
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-6">
          <div className="space-y-4">
            {mockComplianceReports.map((report) => (
              <Card key={report.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${getFrameworkColor(report.framework)}`}>
                        {getFrameworkIcon(report.framework)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{report.framework} Compliance Report</CardTitle>
                        <CardDescription>
                          Generated on {new Date(report.generated_at).toLocaleDateString()}
                        </CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {getComplianceStatusIcon(report.status)}
                      <Badge
                        variant={
                          report.status === 'compliant'
                            ? 'default'
                            : report.status === 'warning'
                            ? 'secondary'
                            : 'destructive'
                        }
                      >
                        {report.status}
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{report.score}%</div>
                      <div className="text-sm text-gray-500">Compliance Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{report.violations}</div>
                      <div className="text-sm text-gray-500">Violations</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600">{report.warnings}</div>
                      <div className="text-sm text-gray-500">Warnings</div>
                    </div>
                    <div className="text-center">
                      <Button size="sm" variant="outline">
                        <Download className="mr-1 h-4 w-4" />
                        Download
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="audit" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <FileText className="h-5 w-5" />
                <span>Audit Trail</span>
              </CardTitle>
              <CardDescription>
                Complete activity log for regulatory compliance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Audit trail coming soon</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Comprehensive audit logging will be available here
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Compliance;
