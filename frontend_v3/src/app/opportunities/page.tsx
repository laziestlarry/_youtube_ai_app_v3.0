'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Opportunity } from '@/lib/types';
import { rankBusinessOpportunities } from '@/ai/flows/rank-business-opportunities';
import { useToast } from '@/hooks/use-toast';
import { fetchBizopOpportunities, fetchBizopSources, refreshBizopCatalog } from '@/lib/bizop';
import { fetchOutcomeSummary, OutcomeSummary } from '@/lib/outcomes';
import { buildBackendUrl } from '@/lib/backend';
import AppHeader from '@/components/app-header';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Activity, ArrowLeft, ExternalLink } from 'lucide-react';
import OpportunityCard from '@/components/opportunity-card';
import { OpportunityListSkeleton } from '@/components/opportunity-skeletons';

export type RankedOpportunity = Opportunity & {
  rank: number;
  rationale: string;
};

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 2,
});

const compactFormatter = new Intl.NumberFormat('en-US', {
  notation: 'compact',
  maximumFractionDigits: 1,
});

const formatCurrency = (value?: number | null) => {
  if (value === null || value === undefined) {
    return '—';
  }
  return currencyFormatter.format(value);
};

const formatCount = (value?: number | null) => {
  if (value === null || value === undefined) {
    return '—';
  }
  return compactFormatter.format(value);
};

export default function OpportunitiesPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [rankedOpportunities, setRankedOpportunities] = useState<RankedOpportunity[] | null>(null);
  const [bizopSources, setBizopSources] = useState<string[]>([]);
  const [selectedSource, setSelectedSource] = useState<string>('all');
  const [useBizop, setUseBizop] = useState(false);
  const [bizopError, setBizopError] = useState<string | null>(null);
  const [outcomeSummary, setOutcomeSummary] = useState<OutcomeSummary | null>(null);
  const [outcomeError, setOutcomeError] = useState<string | null>(null);
  const [isOutcomeLoading, setIsOutcomeLoading] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    const opportunitiesString = localStorage.getItem('discoveredOpportunities');
    if (opportunitiesString) {
      try {
        const opportunities: Opportunity[] = JSON.parse(opportunitiesString);
        if (Array.isArray(opportunities) && opportunities.length > 0) {
          setUseBizop(false);
          rankOpportunities(opportunities);
          return;
        }
      } catch (error) {
        console.error('Failed to parse local opportunities cache.', error);
      }
      localStorage.removeItem('discoveredOpportunities');
    }

    setUseBizop(true);
  }, []);

  useEffect(() => {
    if (!useBizop) {
      return;
    }

    const loadSources = async () => {
      try {
        const sources = await fetchBizopSources();
        setBizopSources(sources);
      } catch (error) {
        console.error(error);
      }
    };

    loadSources();
  }, [useBizop]);

  useEffect(() => {
    if (!useBizop) {
      return;
    }

    const fetchBizops = async () => {
      setBizopError(null);
      setIsLoading(true);
      try {
        const data = await fetchBizopOpportunities({
          source: selectedSource === 'all' ? undefined : selectedSource,
          limit: 200,
        });
        if (data.length > 0) {
          await rankOpportunities(data);
        } else {
          setRankedOpportunities([]);
          setBizopError('BizOp catalog is empty. Run a refresh to import new opportunities.');
          setIsLoading(false);
        }
      } catch (error) {
        console.error(error);
        setRankedOpportunities([]);
        setBizopError('Could not load BizOp opportunities. Confirm the backend is reachable, then retry.');
        setIsLoading(false);
      }
    };

    fetchBizops();
  }, [selectedSource, useBizop]);

  useEffect(() => {
    let isMounted = true;
    const loadOutcomeSummary = async () => {
      setOutcomeError(null);
      setIsOutcomeLoading(true);
      try {
        const summary = await fetchOutcomeSummary();
        if (isMounted) {
          setOutcomeSummary(summary);
        }
      } catch (error) {
        console.error(error);
        if (isMounted) {
          setOutcomeError('Outcome pulse unavailable. Verify the backend or try again.');
        }
      } finally {
        if (isMounted) {
          setIsOutcomeLoading(false);
        }
      }
    };
    loadOutcomeSummary();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleRefreshBizops = async () => {
    setIsRefreshing(true);
    setBizopError(null);
    try {
      const result = await refreshBizopCatalog();
      toast({
        title: 'BizOp Catalog Refreshed',
        description: `Inserted ${result.inserted}, updated ${result.updated}, total ${result.total}.`,
      });
      const data = await fetchBizopOpportunities({
        source: selectedSource === 'all' ? undefined : selectedSource,
        limit: 200,
      });
      if (data.length > 0) {
        await rankOpportunities(data);
      } else {
        setRankedOpportunities([]);
        setBizopError('Refresh completed, but the catalog is still empty.');
        setIsLoading(false);
      }
    } catch (error) {
      console.error(error);
      toast({
        variant: 'destructive',
        title: 'Refresh Failed',
        description: 'Could not refresh BizOp catalog. Please try again.',
      });
      setBizopError('Refresh failed. Confirm the backend is reachable, then retry.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const rankOpportunities = async (opportunities: Opportunity[]) => {
    setIsLoading(true);
    try {
      const result = await rankBusinessOpportunities({
        opportunities,
        focus: 'Maximum profit potential with minimal risk and fastest time-to-market.',
      });
      if (result) {
        // The flow already returns sorted items, but we sort again just in case
        const sorted = result.sort((a, b) => a.rank - b.rank);
        setRankedOpportunities(sorted);
      } else {
        toast({
          variant: 'destructive',
          title: 'Ranking Failed',
          description: 'Could not rank the opportunities. Displaying original list.',
        });
        // Fallback to showing unranked opportunities
        setRankedOpportunities(opportunities.map((o, i) => ({ ...o, rank: i + 1, rationale: 'N/A' })));
      }
    } catch (error) {
      console.error(error);
      toast({
        variant: 'destructive',
        title: 'An Error Occurred',
        description: 'Failed to rank business opportunities. Please try again.',
      });
      // Fallback to showing unranked opportunities
      setRankedOpportunities(opportunities.map((o, i) => ({ ...o, rank: i + 1, rationale: 'N/A' })));
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSelectOpportunity = (opportunity: Opportunity) => {
    // Store selected opportunity and navigate to dashboard
    localStorage.setItem('selectedOpportunity', JSON.stringify(opportunity));
    router.push('/dashboard');
  };

  const handleBackToForm = () => {
    localStorage.removeItem('discoveredOpportunities');
    router.push('/');
  };

  const outcomeHref = buildBackendUrl('/api/outcomes/summary');
  const kpiSummary = outcomeSummary?.kpi?.summary;
  const totalKpis = kpiSummary?.total ?? 0;
  const unknownKpis = kpiSummary?.unknown ?? 0;
  const unknownRatio = totalKpis > 0 ? Math.round((unknownKpis / totalKpis) * 100) : null;
  const hasResults = rankedOpportunities && rankedOpportunities.length > 0;

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AppHeader>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          <Button variant="ghost" size="sm" onClick={handleBackToForm}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Discovery
          </Button>
          <Button variant="outline" size="sm" asChild>
            <Link href="/alexandria">Open Alexandria</Link>
          </Button>
          <Button variant="secondary" size="sm" asChild>
            <a href={outcomeHref} target="_blank" rel="noreferrer">
              Outcomes API <ExternalLink className="ml-2 h-4 w-4" />
            </a>
          </Button>
        </div>
      </AppHeader>
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="flex flex-col gap-8">
          <section className="flex flex-col gap-6">
            <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 className="font-headline text-3xl font-bold tracking-tight">BizOp Command Center</h2>
                <p className="text-muted-foreground">
                  AI-ranked opportunities with revenue signals. Pick the fastest route to real cash flow.
                </p>
              </div>
              {useBizop && (
                <div className="flex flex-wrap items-center gap-3">
                  <Select value={selectedSource} onValueChange={setSelectedSource}>
                    <SelectTrigger className="w-[220px]">
                      <SelectValue placeholder="All sources" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All sources</SelectItem>
                      {bizopSources.map((source) => (
                        <SelectItem key={source} value={source}>
                          {source.replace(/_/g, ' ')}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={handleRefreshBizops} disabled={isRefreshing}>
                    {isRefreshing ? 'Refreshing...' : 'Refresh BizOp'}
                  </Button>
                </div>
              )}
            </div>
            <Card className="border-primary/20">
              <CardHeader className="flex flex-row items-center gap-3">
                <Activity className="h-5 w-5 text-primary" />
                <div>
                  <CardTitle>Outcome Pulse</CardTitle>
                  <CardDescription>Live revenue and KPI telemetry powering the BizOp choices.</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p className="text-xs uppercase text-muted-foreground">Revenue Total</p>
                  <p className="text-2xl font-semibold">
                    {isOutcomeLoading ? 'Loading...' : formatCurrency(outcomeSummary?.revenue?.total)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    24h: {formatCurrency(outcomeSummary?.revenue?.last_24h)} | 7d: {formatCurrency(outcomeSummary?.revenue?.last_7d)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase text-muted-foreground">Momentum</p>
                  <p className="text-2xl font-semibold">
                    {isOutcomeLoading ? 'Loading...' : formatCurrency(outcomeSummary?.revenue?.daily)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    30d: {formatCurrency(outcomeSummary?.revenue?.last_30d)} | MTD: {formatCurrency(outcomeSummary?.revenue?.mtd)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase text-muted-foreground">KPI Coverage</p>
                  <p className="text-2xl font-semibold">
                    {isOutcomeLoading ? 'Loading...' : `${kpiSummary?.on_track ?? 0}/${totalKpis} on track`}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {unknownRatio === null ? 'No KPI coverage yet.' : `${unknownRatio}% unknown KPI signals`}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase text-muted-foreground">Pipeline</p>
                  <p className="text-2xl font-semibold">
                    {isOutcomeLoading ? 'Loading...' : formatCount(outcomeSummary?.pipeline?.bizop_total)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Velocity: {formatCount(outcomeSummary?.pipeline?.workflow_velocity)} / 7d
                  </p>
                </div>
              </CardContent>
              {outcomeError && (
                <CardContent>
                  <p className="text-sm text-destructive">{outcomeError}</p>
                </CardContent>
              )}
            </Card>
          </section>

          {bizopError && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
              {bizopError}
            </div>
          )}

          {isLoading && <OpportunityListSkeleton title="Ranking Opportunities..." />}

          {!isLoading && rankedOpportunities && (
            <div>
              {hasResults ? (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {rankedOpportunities.map((opp) => (
                    <OpportunityCard key={opp.rank} opportunity={opp} onSelect={() => handleSelectOpportunity(opp)} />
                  ))}
                </div>
              ) : (
                <Card className="border-dashed">
                  <CardHeader>
                    <CardTitle>No BizOps Yet</CardTitle>
                    <CardDescription>
                      Run a refresh to pull in new opportunities, or return to discovery to seed ideas manually.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex flex-wrap gap-3">
                    {useBizop && (
                      <Button onClick={handleRefreshBizops} disabled={isRefreshing}>
                        {isRefreshing ? 'Refreshing...' : 'Refresh BizOp'}
                      </Button>
                    )}
                    <Button variant="outline" onClick={handleBackToForm}>
                      Back to Discovery
                    </Button>
                    <Button variant="outline" asChild>
                      <Link href="/alexandria">Review Alexandria Signals</Link>
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
