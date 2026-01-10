import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { Opportunity, Analysis, Strategy, BusinessStructure, ActionPlan, Task, ChartData, ExecutiveBrief } from '@/lib/types';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ArrowLeft, BarChart3, Bot, BrainCircuit, Building2, CheckSquare, Clock, Cpu, DollarSign, FileCog, GanttChart, Gavel, Kanban, Lightbulb, LineChart, Milestone, Scale, Search, ShieldQuestion, Target, User, Users, Users2, Zap } from 'lucide-react';
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis } from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { Progress } from '@/components/ui/progress';
import { ProjectManagementViews } from '@/components/project-management-views';
import ExecutiveBriefDisplay from './executive-brief';
import { cn } from '@/lib/utils';
import { fetchKpiTargets } from '@/lib/kpi';
import { fetchOutcomeSummary, type OutcomeSummary } from '@/lib/outcomes';

interface OpportunityDashboardProps {
  opportunity: Opportunity;
  analysis: Analysis;
  strategy: Strategy;
  structure: BusinessStructure;
  actionPlan: ActionPlan | null;
  chartData: ChartData | null;
  executiveBrief: ExecutiveBrief | null;
  onBack: () => void;
  isPrinting?: boolean;
  children?: React.ReactNode;
}

const chartConfig = {
  revenue: {
    label: 'Revenue',
    color: 'hsl(var(--chart-1))',
  },
};

export default function OpportunityDashboard({ opportunity, analysis, strategy, structure, actionPlan, chartData, executiveBrief, onBack, isPrinting, children }: OpportunityDashboardProps) {
  const initialTasks = actionPlan ? actionPlan.actionPlan.flatMap(category => category.tasks) : [];
  const [tasks, setTasks] = useState(initialTasks);
  const [currentView, setCurrentView] = useState<'list' | 'canvas' | 'kanban' | 'gantt'>('list');
  const [kpiData, setKpiData] = useState<any>(null);
  const [kpiError, setKpiError] = useState<string | null>(null);
  const [outcomeSummary, setOutcomeSummary] = useState<OutcomeSummary | null>(null);
  const [outcomeError, setOutcomeError] = useState<string | null>(null);
  const router = useRouter();

  const okrs = structure.okrs ?? [];
  const advisoryCouncil = structure.advisoryCouncil ?? [];
  const cLevelBoard = structure.cLevelBoard ?? [];
  const projectManagementFramework = structure.projectManagementFramework ?? { methodology: 'TBD', phases: [] };
  const departments = structure.departments ?? [];
  const commander = structure.commander ?? 'Commander details pending.';


  const handleToggleTask = (id: string) => {
    setTasks(currentTasks =>
      currentTasks.map(task =>
        task.id === id ? { ...task, completed: !task.completed } : task
      )
    );
  };
  
  const completedTasks = tasks.filter(task => task.completed).length;
  const totalTasks = tasks.length;
  const progressPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;
  
  const getIconForRole = (role: string) => {
    const lowerRole = role.toLowerCase();
    if (lowerRole.includes('legal')) return <Gavel className="h-5 w-5 text-primary" />;
    if (lowerRole.includes('debat')) return <Scale className="h-5 w-5 text-primary" />;
    if (lowerRole.includes('philosopher') || lowerRole.includes('ethic')) return <BrainCircuit className="h-5 w-5 text-primary" />;
    if (lowerRole.includes('audit')) return <Search className="h-5 w-5 text-primary" />;
    return <User className="h-5 w-5 text-primary" />;
  };

  const handleIgniteGenesis = () => {
    router.push('/build');
  };

  useEffect(() => {
    let isMounted = true;
    fetchKpiTargets()
      .then((data) => {
        if (isMounted) {
          setKpiData(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setKpiError('KPI data is not available yet.');
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    let isMounted = true;
    fetchOutcomeSummary()
      .then((data) => {
        if (isMounted) {
          setOutcomeSummary(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setOutcomeError('Outcome telemetry is not available yet.');
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const topKpis = useMemo(() => {
    const items = Array.isArray(kpiData?.kpis) ? kpiData.kpis : [];
    return items.slice(0, 6);
  }, [kpiData]);

  const formatKpiValue = (value: number | null | undefined, unit: string) => {
    if (value === null || value === undefined) return 'n/a';
    if (unit === 'USD') return `$${value.toLocaleString()}`;
    if (unit === 'ratio') return `${Math.round(value * 1000) / 10}%`;
    return `${value.toLocaleString()} ${unit}`;
  };

  const formatCurrency = (value: number | null | undefined) => {
    if (value === null || value === undefined) return 'n/a';
    return `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
  };

  const progressForKpi = (kpi: any) => {
    if (kpi.actual === null || kpi.actual === undefined || !kpi.target) return 0;
    if (kpi.direction === 'down') {
      const ratio = kpi.target / Math.max(kpi.actual, 0.0001);
      return Math.min(Math.round(ratio * 100), 100);
    }
    const ratio = kpi.actual / kpi.target;
    return Math.min(Math.round(ratio * 100), 100);
  };

  const statusClass = (status: string) => {
    if (status === 'on_track') return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30';
    if (status === 'at_risk') return 'bg-amber-500/10 text-amber-500 border-amber-500/30';
    if (status === 'off_track') return 'bg-rose-500/10 text-rose-500 border-rose-500/30';
    return 'bg-muted text-muted-foreground border-border';
  };

  const actionPlanTabDisabled = !actionPlan;
  const financialsTabDisabled = !actionPlan;

  const analysisAccordionItems = ["demand", "competition", "revenue"];
  const structureAccordionItems = [
      "commander",
      "aicore",
      "c-level-board",
      "advisory-council",
      "pm-framework",
      "departments",
      ...okrs.map((_,i) => `okr-${i}`),
      ...advisoryCouncil.map((_, i) => `advisor-${i}`), 
      ...cLevelBoard.map((_, i) => `clevel-${i}`),
      ...projectManagementFramework.phases.map((_, i) => `phase-${i}`),
      ...departments.map((d) => d.name)
    ];
  const strategyAccordionItems = ["marketing", "operations", "financials", "bmc"];
  const financialAccordionItems = [
      "capex", "opex", "investment",
      ...(actionPlan?.financials.capex.map((_, i) => `capex-${i}`) || []),
      ...(actionPlan?.financials.opex.map((_, i) => `opex-${i}`) || []),
      ...(actionPlan?.financials.investmentOptions.map((_, i) => `invest-${i}`) || [])
    ];
    
  return (
    <div className="animate-in fade-in-50 duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8 print:hidden">
        <div>
          <Button variant="ghost" size="sm" onClick={onBack} className="mb-2">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Opportunities
          </Button>
          <h1 className="font-headline text-3xl md:text-4xl font-bold tracking-tight">{opportunity.opportunityName}</h1>
          <p className="text-muted-foreground mt-1">{opportunity.description}</p>
        </div>
        <Card className="p-3 bg-accent/20 border-accent/30">
          <div className="flex items-center gap-2">
            <Bot className="h-6 w-6 text-accent"/>
            <p className="text-sm font-semibold text-accent-foreground">AI Generated Insights</p>
          </div>
        </Card>
      </div>
      
      <div className="hidden print:block mb-8">
        <h1 className="font-headline text-3xl md:text-4xl font-bold tracking-tight">{opportunity.opportunityName}</h1>
        <p className="text-muted-foreground mt-1 mb-8">{opportunity.description}</p>
      </div>
      
      {executiveBrief && <ExecutiveBriefDisplay brief={executiveBrief} />}

      {actionPlan && (
        <Card className="mb-8 bg-primary/10 border-primary/20 text-center">
            <CardContent className="p-6">
                 <div className="flex flex-col items-center gap-4">
                     <h2 className="font-headline text-2xl font-bold">Blueprint Complete</h2>
                    <p className="text-muted-foreground max-w-xl mx-auto">Your strategic blueprint is ready. The next step is to execute the plan and bring your vision to life.</p>
                    <Button size="lg" onClick={handleIgniteGenesis}>
                        <Zap className="mr-2 h-5 w-5" />
                        Build the Genesis
                    </Button>
                </div>
            </CardContent>
        </Card>
      )}

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="font-headline text-2xl flex items-center gap-2">
            <LineChart className="h-5 w-5 text-primary" /> Outcome Pulse
          </CardTitle>
          <CardDescription>
            Live execution signals for revenue, pipeline velocity, and KPI readiness.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {outcomeError && (
            <Alert>
              <AlertTitle>Outcome telemetry offline</AlertTitle>
              <AlertDescription>{outcomeError}</AlertDescription>
            </Alert>
          )}

          {outcomeSummary && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="rounded-lg border border-border p-3">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Revenue total</div>
                  <div className="text-xl font-semibold">{formatCurrency(outcomeSummary.revenue.total)}</div>
                </div>
                <div className="rounded-lg border border-border p-3">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Last 24h</div>
                  <div className="text-xl font-semibold">{formatCurrency(outcomeSummary.revenue.last_24h)}</div>
                </div>
                <div className="rounded-lg border border-border p-3">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Last 7 days</div>
                  <div className="text-xl font-semibold">{formatCurrency(outcomeSummary.revenue.last_7d)}</div>
                </div>
                <div className="rounded-lg border border-border p-3">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Pipeline velocity</div>
                  <div className="text-xl font-semibold">{outcomeSummary.pipeline.workflow_velocity}</div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="rounded-lg border border-border p-3 space-y-2">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Top revenue sources</div>
                  {outcomeSummary.revenue.top_sources.length === 0 ? (
                    <div className="text-sm text-muted-foreground">No revenue history yet.</div>
                  ) : (
                    outcomeSummary.revenue.top_sources.map((item) => (
                      <div key={item.source} className="flex items-center justify-between text-sm">
                        <span className="truncate pr-2">{item.source}</span>
                        <span className="font-semibold">{formatCurrency(item.amount)}</span>
                      </div>
                    ))
                  )}
                </div>
                <div className="rounded-lg border border-border p-3 space-y-2">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">Pipeline readiness</div>
                  <div className="text-sm">
                    BizOp catalog size: <span className="font-semibold">{outcomeSummary.pipeline.bizop_total}</span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    KPI telemetry updated: {outcomeSummary.kpi.updated_at ?? 'pending'}
                  </div>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="font-headline text-2xl flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" /> KPI Execution Engine
          </CardTitle>
          <CardDescription>
            Live KPI targets mapped to culture, workflows, and revenue streams.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {kpiError && (
            <Alert>
              <AlertTitle>KPI feed offline</AlertTitle>
              <AlertDescription>{kpiError}</AlertDescription>
            </Alert>
          )}

          {kpiData?.summary && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {['on_track', 'at_risk', 'off_track', 'unknown'].map((key) => (
                <div key={key} className="rounded-lg border border-border p-3">
                  <div className="text-xs uppercase tracking-wider text-muted-foreground">{key.replace('_', ' ')}</div>
                  <div className="text-xl font-semibold">{kpiData.summary[key]}</div>
                </div>
              ))}
              <div className="rounded-lg border border-border p-3">
                <div className="text-xs uppercase tracking-wider text-muted-foreground">total</div>
                <div className="text-xl font-semibold">{kpiData.summary.total}</div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {topKpis.map((kpi: any) => (
              <div key={kpi.id} className="rounded-lg border border-border p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold">{kpi.name}</div>
                    <div className="text-xs text-muted-foreground">{kpi.category} • {kpi.owner || 'Owner TBD'}</div>
                  </div>
                  <span className={`text-xs border px-2 py-1 rounded-full ${statusClass(kpi.status)}`}>
                    {kpi.status_label}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Target: {formatKpiValue(kpi.target, kpi.unit)}</span>
                  <span>Actual: {formatKpiValue(kpi.actual, kpi.unit)}</span>
                </div>
                <Progress value={progressForKpi(kpi)} />
              </div>
            ))}
          </div>

          <div className="rounded-lg border border-border p-4 text-sm text-muted-foreground">
            Operating references: <span className="font-mono">docs/OPERATING_INDEX.md</span>, <span className="font-mono">docs/CULTURE_OPERATING_SYSTEM.md</span>, <span className="font-mono">docs/KPI_EXECUTION_ENGINE.md</span>.
          </div>
        </CardContent>
      </Card>


      <Tabs defaultValue="analysis" className={cn("w-full", isPrinting && 'print-visible-tabs')}>
        <TabsList className="grid w-full grid-cols-1 sm:w-auto sm:grid-cols-3 lg:grid-cols-5 print:hidden">
          <TabsTrigger value="analysis">
            <LineChart className="mr-2 h-4 w-4" /> Market Analysis
          </TabsTrigger>
          <TabsTrigger value="structure">
            <Building2 className="mr-2 h-4 w-4" /> Org Structure
          </TabsTrigger>
          <TabsTrigger value="strategy">
            <BrainCircuit className="mr-2 h-4 w-4" /> Business Strategy
          </TabsTrigger>
          <TabsTrigger value="action-plan" disabled={actionPlanTabDisabled}>
            <CheckSquare className="mr-2 h-4 w-4" /> Action Plan
          </TabsTrigger>
          <TabsTrigger value="financials" disabled={financialsTabDisabled}>
             <DollarSign className="mr-2 h-4 w-4" /> Financials
          </TabsTrigger>
        </TabsList>

        <div className={cn(isPrinting && 'print-visible-tabs')}>
        <TabsContent value="analysis" className="mt-6 print:break-after-page">
          <div className="space-y-6">
            <Card className="print:border-none print:shadow-none">
              <CardHeader>
                <CardTitle className="font-headline text-2xl">Market Analysis</CardTitle>
                <CardDescription className="print:hidden">
                    High-level market assessment. Expand each section to see the detailed AI analysis.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Accordion type="multiple" defaultValue={isPrinting ? analysisAccordionItems : undefined} className={cn("w-full space-y-4", isPrinting && "print-visible-accordion")}>
                    <AccordionItem value="demand" className="border rounded-lg">
                        <AccordionTrigger className="p-4 font-semibold text-lg flex items-center gap-3">
                            <Users className="h-5 w-5 text-primary" /> Demand Forecast
                        </AccordionTrigger>
                        <AccordionContent className="p-4 pt-0 text-muted-foreground">
                            {analysis.demandForecast}
                        </AccordionContent>
                    </AccordionItem>
                    <AccordionItem value="competition" className="border rounded-lg">
                        <AccordionTrigger className="p-4 font-semibold text-lg flex items-center gap-3">
                            <Target className="h-5 w-5 text-primary" /> Competitive Landscape
                        </AccordionTrigger>
                        <AccordionContent className="p-4 pt-0 text-muted-foreground">
                            {analysis.competitiveLandscape}
                        </AccordionContent>
                    </AccordionItem>
                     <AccordionItem value="revenue" className="border rounded-lg">
                        <AccordionTrigger className="p-4 font-semibold text-lg flex items-center gap-3">
                            <DollarSign className="h-5 w-5 text-primary" /> Potential Revenue
                        </AccordionTrigger>
                        <AccordionContent className="p-4 pt-0 text-muted-foreground">
                            {analysis.potentialRevenue}
                        </AccordionContent>
                    </AccordionItem>
                </Accordion>
              </CardContent>
            </Card>
            <Card className="print:border-none print:shadow-none">
              <CardHeader>
                <CardTitle className="font-headline">AI-Generated Revenue Projection</CardTitle>
              </CardHeader>
              <CardContent className="pl-2">
                <ChartContainer config={chartConfig} className="h-[250px] w-full">
                  <BarChart accessibilityLayer data={chartData || []}>
                    <XAxis dataKey="month" tickLine={false} axisLine={false} tickMargin={8} fontSize={12} />
                    <YAxis tickLine={false} axisLine={false} tickMargin={8} fontSize={12} tickFormatter={(value) => `$${new Intl.NumberFormat('en-US', { notation: 'compact', compactDisplay: 'short' }).format(value)}`} />
                    <ChartTooltip 
                        cursor={false} 
                        content={<ChartTooltipContent 
                            formatter={(value) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(value as number)}
                        />} 
                    />
                    <Bar dataKey="revenue" fill="var(--color-revenue)" radius={4} />
                  </BarChart>
                </ChartContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="structure" className="mt-6 print:break-after-page">
            <div className="space-y-6">
                 <Card className="print:border-none print:shadow-none">
                    <CardHeader>
                        <CardTitle className="font-headline text-2xl">Organizational Blueprint</CardTitle>
                        <CardDescription className="print:hidden">
                            This is an AI-generated organizational structure designed for automation and efficiency.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <Accordion type="multiple" defaultValue={isPrinting ? structureAccordionItems: undefined} className={cn(isPrinting && "print-visible-accordion")}>
                            <AccordionItem value="okrs">
                                <AccordionTrigger>Corporate OKRs</AccordionTrigger>
                                <AccordionContent className="space-y-4">
                                     {okrs.map((okr, index) => (
                                        <div key={index} className="p-4 border rounded-lg bg-card/50">
                                        <h4 className="font-semibold text-lg">{okr.objective}</h4>
                                        <ul className="list-disc list-inside mt-2 text-muted-foreground space-y-1">
                                            {okr.keyResults.map((kr, i) => <li key={i}>{kr}</li>)}
                                        </ul>
                                        </div>
                                    ))}
                                </AccordionContent>
                            </AccordionItem>
                            
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-6">
                                <div className="space-y-6">
                                    <AccordionItem value="commander">
                                        <AccordionTrigger>
                                            <div className="flex items-center gap-3 font-headline">
                                                <User className="h-6 w-6 text-primary" />
                                                Multi-Layered Commander
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent>
                                            <p className="text-muted-foreground">{commander}</p>
                                        </AccordionContent>
                                    </AccordionItem>
                                     <AccordionItem value="aicore">
                                        <AccordionTrigger>
                                            <div className="flex items-center gap-3 font-headline">
                                                <Cpu className="h-6 w-6 text-primary" />
                                                AI-Core Base
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent>
                                            <p className="text-muted-foreground">{structure.aiCore}</p>
                                        </AccordionContent>
                                    </AccordionItem>
                                    <AccordionItem value="advisory-council">
                                        <AccordionTrigger>
                                            <div className="flex items-center gap-3 font-headline">
                                                <ShieldQuestion className="h-6 w-6 text-primary" />
                                                Advisory Council
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent>
                                            <Accordion type="multiple" defaultValue={isPrinting ? advisoryCouncil.map((_,i) => `advisor-${i}`) : undefined} className={cn("w-full", isPrinting && "print-visible-accordion")}>
                                                {advisoryCouncil.map((advisor, index) => (
                                                    <AccordionItem key={index} value={`advisor-${index}`}>
                                                        <AccordionTrigger className="text-base font-semibold">
                                                        <div className="flex items-center gap-3">
                                                            {getIconForRole(advisor.role)}
                                                            {advisor.role}
                                                        </div>
                                                        </AccordionTrigger>
                                                        <AccordionContent className="pt-2 text-sm">
                                                        <p className="text-muted-foreground">{advisor.description}</p>
                                                        </AccordionContent>
                                                    </AccordionItem>
                                                ))}
                                            </Accordion>
                                        </AccordionContent>
                                    </AccordionItem>
                                </div>
                                <div className="space-y-6">
                                     <AccordionItem value="c-level-board">
                                        <AccordionTrigger>
                                            <div className="flex items-center gap-3 font-headline">
                                                <Users2 className="h-6 w-6 text-primary" />
                                                C-Level Board
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent>
                                            <Accordion type="multiple" defaultValue={isPrinting ? cLevelBoard.map((_,i) => `clevel-${i}`) : undefined} className={cn("w-full", isPrinting && "print-visible-accordion")}>
                                                {cLevelBoard.map((role, index) => (
                                                    <AccordionItem key={index} value={`clevel-${index}`}>
                                                        <AccordionTrigger className="text-base font-semibold">
                                                            {role.role}
                                                        </AccordionTrigger>
                                                        <AccordionContent className="pt-2 text-sm text-muted-foreground">
                                                            {role.description}
                                                        </AccordionContent>
                                                    </AccordionItem>
                                                ))}
                                            </Accordion>
                                        </AccordionContent>
                                    </AccordionItem>
                                    <AccordionItem value="pm-framework">
                                        <AccordionTrigger>
                                            <div className="flex items-center gap-3 font-headline">
                                                <Milestone className="h-6 w-6 text-primary" />
                                                Project Management Framework
                                            </div>
                                        </AccordionTrigger>
                                        <AccordionContent>
                                            <p className="font-semibold mb-2">{projectManagementFramework.methodology}</p>
                                            <Accordion type="multiple" defaultValue={isPrinting ? projectManagementFramework.phases.map((_,i) => `phase-${i}`) : undefined} className={cn("w-full", isPrinting && "print-visible-accordion")}>
                                                {projectManagementFramework.phases.map((phase, index) => (
                                                    <AccordionItem key={index} value={`phase-${index}`}>
                                                        <AccordionTrigger className="text-base font-semibold">{phase.phaseName}</AccordionTrigger>
                                                        <AccordionContent className="pt-2 text-sm space-y-3">
                                                            <p className="text-muted-foreground">{phase.description}</p>
                                                            <ul className="list-disc list-inside text-muted-foreground space-y-1">
                                                                {phase.keyActivities.map((activity, i) => <li key={i}>{activity}</li>)}
                                                            </ul>
                                                        </AccordionContent>
                                                    </AccordionItem>
                                                ))}
                                            </Accordion>
                                        </AccordionContent>
                                    </AccordionItem>
                                </div>
                            </div>

                            <AccordionItem value="departments">
                                <AccordionTrigger className="font-headline">AI-Powered Departments</AccordionTrigger>
                                <AccordionContent>
                                    <Accordion type="multiple" defaultValue={isPrinting ? departments.map(d => d.name) : undefined} className={cn("w-full", isPrinting && "print-visible-accordion")}>
                                        {departments.map((dept, index) => (
                                            <AccordionItem key={index} value={dept.name}>
                                                <AccordionTrigger className="text-lg font-semibold">{dept.name}</AccordionTrigger>
                                                <AccordionContent className="pt-2 text-base space-y-6">
                                                    <div>
                                                        <h4 className="font-semibold text-foreground mb-1">Function</h4>
                                                        <p className="text-muted-foreground whitespace-pre-line">{dept.function}</p>
                                                    </div>
                                                    <div>
                                                        <h4 className="font-semibold text-foreground mb-1">AI Integration</h4>
                                                        <p className="text-muted-foreground whitespace-pre-line">{dept.aiIntegration}</p>
                                                    </div>
                                                    <div>
                                                        <h4 className="font-semibold text-foreground mb-2">Department KPIs</h4>
                                                        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                                                        {dept.kpis.map((kpi, i) => (
                                                            <div key={i} className="p-3 border rounded-lg bg-background/50">
                                                            <h5 className="font-bold">{kpi.kpi}</h5>
                                                            <p className="text-sm text-muted-foreground mt-1">Target: {kpi.target}</p>
                                                            </div>
                                                        ))}
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <h4 className="font-semibold text-foreground mb-2">AI Staff & Personas</h4>
                                                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                                                        {dept.staff.map((staff, i) => (
                                                            <div key={i} className="p-4 border rounded-lg bg-background/50">
                                                            <h5 className="font-bold">{staff.role}</h5>
                                                            <p className="text-sm text-muted-foreground italic mt-1">{staff.persona}</p>
                                                            </div>
                                                        ))}
                                                        </div>
                                                    </div>
                                                </AccordionContent>
                                            </AccordionItem>
                                        ))}
                                    </Accordion>
                                </AccordionContent>
                            </AccordionItem>
                        </Accordion>
                    </CardContent>
                 </Card>
            </div>
        </TabsContent>
        <TabsContent value="strategy" className="mt-6 print:break-after-page">
           <div className="space-y-6">
            <Card className="print:border-none print:shadow-none">
                <CardHeader>
                    <CardTitle className="font-headline text-2xl">Business Strategy</CardTitle>
                    <CardDescription className="print:hidden">
                        This automated strategy provides a starting point. Adapt these tactics and workflows to your specific goals and resources.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <Accordion type="multiple" defaultValue={isPrinting ? strategyAccordionItems : undefined} className={cn(isPrinting && "print-visible-accordion")}>
                        {actionPlan && (
                            <AccordionItem value="bmc">
                                <AccordionTrigger className="font-headline">Business Model Canvas</AccordionTrigger>
                                <AccordionContent>
                                    <ProjectManagementViews actionPlan={actionPlan} view="canvas" />
                                </AccordionContent>
                            </AccordionItem>
                        )}
                        <AccordionItem value="marketing">
                            <AccordionTrigger className="text-lg font-semibold">
                            <div className="flex items-center gap-3">
                                <BarChart3 className="h-5 w-5 text-primary" />
                                Marketing Tactics
                            </div>
                            </AccordionTrigger>
                            <AccordionContent className="pt-2 text-base text-muted-foreground whitespace-pre-line">
                            {strategy.businessStrategy.marketingTactics}
                            </AccordionContent>
                        </AccordionItem>
                        <AccordionItem value="operations">
                            <AccordionTrigger className="text-lg font-semibold">
                            <div className="flex items-center gap-3">
                                <FileCog className="h-5 w-5 text-primary" />
                                Operational Workflows
                            </div>
                            </AccordionTrigger>
                            <AccordionContent className="pt-2 text-base text-muted-foreground whitespace-pre-line">
                            {strategy.businessStrategy.operationalWorkflows || strategy.businessStrategy.operationalPlan}
                            </AccordionContent>
                        </AccordionItem>
                        <AccordionItem value="financials">
                            <AccordionTrigger className="text-lg font-semibold">
                            <div className="flex items-center gap-3">
                                <DollarSign className="h-5 w-5 text-primary" />
                                Financial Forecasts
                            </div>
                            </AccordionTrigger>
                            <AccordionContent className="pt-2 text-base text-muted-foreground whitespace-pre-line">
                            {strategy.businessStrategy.financialForecasts}
                            </AccordionContent>
                        </AccordionItem>
                    </Accordion>
                </CardContent>
            </Card>
           </div>
        </TabsContent>
         <TabsContent value="action-plan" className="mt-6 print:break-after-page">
          {actionPlan && (
            <div className="space-y-6">
                <Card className="print:border-none print:shadow-none">
                    <CardHeader>
                         <CardTitle className="font-headline text-2xl">Action Plan</CardTitle>
                         <CardDescription className="print:hidden">
                            This is your AI-generated to-do list. Use the controls to switch between List, Kanban, and Gantt views.
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                         <Alert variant="destructive">
                            <Clock className="h-4 w-4" />
                            <AlertTitle>Critical Path Estimate</AlertTitle>
                            <AlertDescription>
                                The AI has identified <strong>`{actionPlan.criticalPath.taskTitle}`</strong> as the most time-consuming task, with an estimated duration of <strong>{actionPlan.criticalPath.timeEstimate}</strong>. Prioritizing this will be key to timely project completion.
                            </AlertDescription>
                        </Alert>
                        <Card>
                        <CardHeader>
                            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                            <div className="flex-1">
                                <CardTitle className="font-headline">Implementation Progress</CardTitle>
                                <div className="flex items-center gap-4 pt-2">
                                <Progress value={progressPercentage} className="w-full" />
                                <span className="text-sm font-semibold text-muted-foreground whitespace-nowrap">
                                    {completedTasks} / {totalTasks} Tasks
                                </span>
                                </div>
                            </div>
                            <div className="flex items-center gap-2 print:hidden">
                                <Button variant={currentView === 'list' ? 'default' : 'outline'} size="sm" onClick={() => setCurrentView('list')}>
                                    <CheckSquare className="mr-2 h-4 w-4" /> List
                                </Button>
                                <Button variant={currentView === 'kanban' ? 'default' : 'outline'} size="sm" onClick={() => setCurrentView('kanban')}>
                                    <Kanban className="mr-2 h-4 w-4" /> Board
                                </Button>
                                <Button variant={currentView === 'gantt' ? 'default' : 'outline'} size="sm" onClick={() => setCurrentView('gantt')}>
                                    <GanttChart className="mr-2 h-4 w-4" /> Gantt
                                </Button>
                            </div>
                            </div>
                        </CardHeader>
                        <CardContent className="p-0">
                            <ProjectManagementViews actionPlan={actionPlan} view={currentView} tasks={tasks} onToggleTask={handleToggleTask} />
                        </CardContent>
                        </Card>
                    </CardContent>
                </Card>
            </div>
          )}
        </TabsContent>
         <TabsContent value="financials" className="mt-6 print:break-after-page">
            {actionPlan && (
                <div className="space-y-6">
                    <Card className="print:border-none print:shadow-none">
                         <CardHeader>
                            <CardTitle className="font-headline text-2xl">Financials</CardTitle>
                            <CardDescription className="print:hidden">
                                These are AI-generated financial estimates based on the business strategy.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                             <Accordion type="multiple" defaultValue={isPrinting ? financialAccordionItems : undefined} className={cn(isPrinting && "print-visible-accordion")}>
                                <AccordionItem value="capex">
                                    <AccordionTrigger className="font-headline">Capital Expenditures (CAPEX)</AccordionTrigger>
                                    <AccordionContent>
                                        <CardDescription>One-time costs to get the business started.</CardDescription>
                                        <Accordion type="multiple" defaultValue={isPrinting ? actionPlan.financials.capex.map((_, i) => `capex-${i}`) : undefined} className={cn("w-full mt-4", isPrinting && "print-visible-accordion")}>
                                            {actionPlan.financials.capex.map((item, index) => (
                                                <AccordionItem key={index} value={`capex-${index}`}>
                                                    <AccordionTrigger className="text-base font-semibold">
                                                    <div className="flex justify-between w-full pr-4">
                                                        <span>{item.item}</span>
                                                        <span className="text-primary">{item.amount}</span>
                                                    </div>
                                                    </AccordionTrigger>
                                                    <AccordionContent className="pt-2 text-sm text-muted-foreground">
                                                    {item.justification}
                                                    </AccordionContent>
                                                </AccordionItem>
                                            ))}
                                        </Accordion>
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="opex">
                                    <AccordionTrigger className="font-headline">Operational Expenditures (OPEX)</AccordionTrigger>
                                    <AccordionContent>
                                        <CardDescription>Recurring monthly or annual costs to run the business.</CardDescription>
                                        <Accordion type="multiple" defaultValue={isPrinting ? actionPlan.financials.opex.map((_, i) => `opex-${i}`) : undefined} className={cn("w-full mt-4", isPrinting && "print-visible-accordion")}>
                                            {actionPlan.financials.opex.map((item, index) => (
                                                <AccordionItem key={index} value={`opex-${index}`}>
                                                    <AccordionTrigger className="text-base font-semibold">
                                                    <div className="flex justify-between w-full pr-4">
                                                        <span>{item.item}</span>
                                                        <span className="text-primary">{item.amount}</span>
                                                    </div>
                                                    </AccordionTrigger>
                                                    <AccordionContent className="pt-2 text-sm text-muted-foreground">
                                                    {item.justification}
                                                    </AccordionContent>
                                                </AccordionItem>
                                            ))}
                                        </Accordion>
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="investment">
                                    <AccordionTrigger className="font-headline">Investment Options</AccordionTrigger>
                                    <AccordionContent className="space-y-4">
                                        <CardDescription>Potential ways to fund your new venture.</CardDescription>
                                        {actionPlan.financials.investmentOptions.map((option, index) => (
                                            <div key={index} className="p-4 border rounded-lg bg-card/50">
                                                <h4 className="font-semibold text-lg">{option.type} - <span className="text-primary">{option.amount}</span></h4>
                                                <p className="text-muted-foreground mt-2">{option.description}</p>
                                            </div>
                                        ))}
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </CardContent>
                    </Card>
                </div>
            )}
        </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
