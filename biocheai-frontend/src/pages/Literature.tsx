import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { literatureApi } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import {
  BookOpen,
  Search,
  FileText,
  Lightbulb,
  ExternalLink,
  Loader2,
  Brain,
  Network,
} from 'lucide-react';

const Literature: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [selectedPapers, setSelectedPapers] = useState<string[]>([]);
  const [researchArea, setResearchArea] = useState('');

  const searchMutation = useMutation({
    mutationFn: ({ query, maxResults }: { query: string; maxResults: number }) =>
      literatureApi.search(query, ['pubmed'], maxResults),
    onSuccess: (data) => {
      toast.success(`Found ${data.length} relevant papers`);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to search literature');
    },
  });

  const summarizeMutation = useMutation({
    mutationFn: literatureApi.summarize,
    onSuccess: () => {
      toast.success('AI-powered literature summary is ready');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to generate summary');
    },
  });

  const hypothesesMutation = useMutation({
    mutationFn: ({ literatureIds, researchArea }: { literatureIds: string[]; researchArea: string }) =>
      literatureApi.generateHypotheses(literatureIds, researchArea),
    onSuccess: () => {
      toast.success('AI-generated research hypotheses are ready');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.error || 'Failed to generate hypotheses');
    },
  });

  const handleSearch = () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    searchMutation.mutate({ query: searchQuery, maxResults });
  };

  const handleSummarize = () => {
    if (selectedPapers.length === 0) {
      toast.error('Please select papers to summarize');
      return;
    }

    summarizeMutation.mutate(selectedPapers);
  };

  const handleGenerateHypotheses = () => {
    if (selectedPapers.length === 0) {
      toast.error('Please select papers for hypothesis generation');
      return;
    }

    if (!researchArea.trim()) {
      toast.error('Please specify your research area');
      return;
    }

    hypothesesMutation.mutate({ literatureIds: selectedPapers, researchArea });
  };

  const togglePaperSelection = (paperId: string) => {
    setSelectedPapers(prev =>
      prev.includes(paperId)
        ? prev.filter(id => id !== paperId)
        : [...prev, paperId]
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Literature Intelligence</h1>
        <p className="text-gray-600 mt-1">
          Search, analyze, and generate insights from scientific literature
        </p>
      </div>

      <Tabs defaultValue="search" className="space-y-6">
        <TabsList>
          <TabsTrigger value="search">Literature Search</TabsTrigger>
          <TabsTrigger value="analysis">Analysis & Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="search" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="h-5 w-5" />
                <span>Search Literature</span>
              </CardTitle>
              <CardDescription>
                Search across PubMed and other scientific databases
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <Label htmlFor="search-query">Search Query</Label>
                  <Input
                    id="search-query"
                    placeholder="e.g., CRISPR gene editing cancer therapy"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="max-results">Max Results</Label>
                  <Input
                    id="max-results"
                    type="number"
                    placeholder="10"
                    value={maxResults}
                    onChange={(e) => setMaxResults(parseInt(e.target.value) || 10)}
                  />
                </div>
              </div>

              <Button
                onClick={handleSearch}
                disabled={searchMutation.isPending}
                className="w-full"
              >
                {searchMutation.isPending ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Searching Literature...
                  </>
                ) : (
                  <>
                    <BookOpen className="mr-2 h-4 w-4" />
                    Search Literature
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {searchMutation.data && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center space-x-2">
                    <FileText className="h-5 w-5" />
                    <span>Search Results</span>
                  </span>
                  <Badge variant="outline">
                    {searchMutation.data.length} papers found
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Select papers for analysis and hypothesis generation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {searchMutation.data.map((paper) => (
                    <div
                      key={paper.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedPapers.includes(paper.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => togglePaperSelection(paper.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900 mb-2">{paper.title}</h4>
                          <p className="text-sm text-gray-600 mb-2">
                            {paper.authors.join(', ')} • {paper.journal} • {paper.publication_date}
                          </p>
                          <p className="text-sm text-gray-700 line-clamp-3">{paper.abstract}</p>
                        </div>
                        <div className="ml-4 flex items-center space-x-2">
                          {paper.doi && (
                            <a
                              href={`https://doi.org/${paper.doi}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800"
                              onClick={(e) => e.stopPropagation()}
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          )}
                          <input
                            type="checkbox"
                            checked={selectedPapers.includes(paper.id)}
                            onChange={() => togglePaperSelection(paper.id)}
                            className="h-4 w-4 text-blue-600"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>AI Summarization</span>
                </CardTitle>
                <CardDescription>
                  Generate comprehensive summaries of selected papers
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm text-gray-600">
                  Selected papers: {selectedPapers.length}
                </div>
                
                <Button
                  onClick={handleSummarize}
                  disabled={summarizeMutation.isPending || selectedPapers.length === 0}
                  className="w-full"
                >
                  {summarizeMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating Summary...
                    </>
                  ) : (
                    <>
                      <FileText className="mr-2 h-4 w-4" />
                      Generate AI Summary
                    </>
                  )}
                </Button>

                {summarizeMutation.data && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h4 className="font-medium mb-2">AI-Generated Summary</h4>
                    <p className="text-sm text-gray-700">{summarizeMutation.data}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Lightbulb className="h-5 w-5" />
                  <span>Hypothesis Generation</span>
                </CardTitle>
                <CardDescription>
                  Generate research hypotheses based on literature analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="research-area">Research Area</Label>
                  <Input
                    id="research-area"
                    placeholder="e.g., cancer immunotherapy"
                    value={researchArea}
                    onChange={(e) => setResearchArea(e.target.value)}
                  />
                </div>

                <Button
                  onClick={handleGenerateHypotheses}
                  disabled={hypothesesMutation.isPending || selectedPapers.length === 0}
                  className="w-full"
                >
                  {hypothesesMutation.isPending ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating Hypotheses...
                    </>
                  ) : (
                    <>
                      <Lightbulb className="mr-2 h-4 w-4" />
                      Generate Hypotheses
                    </>
                  )}
                </Button>

                {hypothesesMutation.data && (
                  <div className="mt-4 space-y-2">
                    <h4 className="font-medium">Generated Hypotheses</h4>
                    {hypothesesMutation.data.map((hypothesis, index) => (
                      <div key={index} className="p-3 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-700">{hypothesis}</p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Network className="h-5 w-5" />
                <span>Knowledge Graph</span>
              </CardTitle>
              <CardDescription>
                Visualize relationships between research concepts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Network className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Knowledge Graph Visualization</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Interactive knowledge graph will be displayed here based on selected literature
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Literature;
