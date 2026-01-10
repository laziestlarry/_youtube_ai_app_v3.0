'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { analyzeMarketOpportunity } from '@/ai/flows/analyze-market-opportunity';
import { generateBusinessStructure } from '@/ai/flows/generate-business-structure';
import { buildAutomatedBusinessStrategy } from '@/ai/flows/build-automated-business-strategy';
import { extractTasksFromStrategy } from '@/ai/flows/extract-tasks-from-strategy';
import { generateBuildModeAdvice } from '@/ai/flows/generate-build-mode-advice';
import { generateChartData } from '@/ai/flows/generate-chart-data';
import { generateExecutiveBrief } from '@/ai/flows/generate-executive-brief';
import type { Opportunity, Analysis, Strategy, BusinessStructure, ActionPlan, BuildModeAdvice, ChartData, ExecutiveBrief } from '@/lib/types';
import AppHeader from '@/components/app-header';
import OpportunityDashboard from '@/components/opportunity-dashboard';
import { OpportunityDashboardSkeleton } from '@/components/opportunity-skeletons';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Bot, Rocket, Printer, Loader2 } from 'lucide-react';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import BuildModeSelector from '@/components/build-mode-selector';
import { StepProgressBar } from '@/components/ui/progress-bar';

type Step = 'initial' | 'analysis' | 'strategy' | 'advice' | 'finalizing' | 'done';

const AnalysisStep = ({ analysis, structure, onNext, isLoading }: { analysis: Analysis | null, structure: BusinessStructure | null, onNext: () => void, isLoading: boolean }) => (
    <Card className="animate-in fade-in-50">
        <CardHeader>
            <CardTitle>Step 1: Market & Organizational Analysis</CardTitle>
            <CardDescription>The AI has analyzed the market and proposed a corporate structure.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
            <div className="p-4 border rounded-lg">
                <h3 className="font-semibold">Market Analysis Summary</h3>
                <p className="text-sm text-muted-foreground mt-1">{analysis?.demandForecast.substring(0, 150)}...</p>
            </div>
            <div className="p-4 border rounded-lg">
                <h3 className="font-semibold">Organizational Structure</h3>
                <p className="text-sm text-muted-foreground mt-1">{structure?.aiCore.substring(0, 150)}...</p>
            </div>
            <Button onClick={onNext} disabled={isLoading}>
                {isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating Strategy...</> : "Next: Generate Business Strategy"}
            </Button>
        </CardContent>
    </Card>
);

const StrategyStep = ({ strategy, onNext, isLoading }: { strategy: Strategy | null, onNext: () => void, isLoading: boolean }) => (
     <Card className="animate-in fade-in-50">
        <CardHeader>
            <CardTitle>Step 2: Business Strategy</CardTitle>
            <CardDescription>A high-level business strategy has been generated.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
             <div className="p-4 border rounded-lg">
                <h3 className="font-semibold">Strategic Pillars</h3>
                <p className="text-sm text-muted-foreground mt-1">{strategy?.businessStrategy.marketingTactics.substring(0, 150)}...</p>
            </div>
            <Button onClick={onNext} disabled={isLoading}>
                {isLoading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating Advice...</> : "Next: Generate Build Advice"}
            </Button>
        </CardContent>
    </Card>
);

export default function DashboardPage() {
  const [currentStep, setCurrentStep] = useState<Step>('initial');
  const [isLoading, setIsLoading] = useState(false);
  const [isPrinting, setIsPrinting] = useState(false);
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [structure, setStructure] = useState<BusinessStructure | null>(null);
  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [buildModeAdvice, setBuildModeAdvice] = useState<BuildModeAdvice | null>(null);
  const [actionPlan, setActionPlan] = useState<ActionPlan | null>(null);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [executiveBrief, setExecutiveBrief] = useState<ExecutiveBrief | null>(null);
  const { toast } = useToast();
  const router = useRouter();

  useEffect(() => {
    const opportunityString = localStorage.getItem('selectedOpportunity');
    if (!opportunityString) {
      router.push('/');
      return;
    }
    const opportunity = JSON.parse(opportunityString);
    setSelectedOpportunity(opportunity);

    const storedPlan = localStorage.getItem(`plan_${opportunity.opportunityName}`);
    if (storedPlan) {
      const { analysis, structure, strategy, actionPlan, chartData, executiveBrief, buildModeAdvice } = JSON.parse(storedPlan);
      setAnalysis(analysis);
      setStructure(structure);
      setStrategy(strategy);
      setBuildModeAdvice(buildModeAdvice);
      setActionPlan(actionPlan);
      setChartData(chartData);
      setExecutiveBrief(executiveBrief);
      setCurrentStep('done');
    }
  }, [router]);

  const handleError = (error: any, title: string, description: string) => {
    console.error(error);
    toast({ variant: 'destructive', title, description });
    setCurrentStep('initial');
    setIsLoading(false);
  };

  const handleStartAnalysis = async () => {
    if (!selectedOpportunity) return;
    try {
      setIsLoading(true);
      const [analysisResult, structureResult] = await Promise.all([
        analyzeMarketOpportunity({ opportunityDescription: selectedOpportunity.description }),
        generateBusinessStructure({
          opportunityName: selectedOpportunity.opportunityName,
          opportunityDescription: selectedOpportunity.description,
        })
      ]);
      setAnalysis(analysisResult);
      setStructure(structureResult);
      setCurrentStep('analysis');
    } catch (error) {
      handleError(error, 'Analysis Failed', 'Failed to run initial analysis.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleGenerateStrategy = async () => {
    if (!analysis) return;
    try {
        setIsLoading(true);
        const marketAnalysisString = `Demand: ${analysis.demandForecast}, Competition: ${analysis.competitiveLandscape}, Revenue: ${analysis.potentialRevenue}`;
        const strategyResult = await buildAutomatedBusinessStrategy({ marketAnalysis: marketAnalysisString });
        setStrategy(strategyResult);
        setCurrentStep('strategy');
    } catch (error) {
        handleError(error, 'Strategy Generation Failed', 'Failed to build business strategy.');
    } finally {
        setIsLoading(false);
    }
  };

  const handleGenerateAdvice = async () => {
    if (!strategy) return;
    try {
        setIsLoading(true);
        const [adviceResult, chartDataResult] = await Promise.all([
            generateBuildModeAdvice({ businessStrategy: strategy.businessStrategy }),
            generateChartData({ financialForecasts: strategy.businessStrategy.financialForecasts })
        ]);
        setBuildModeAdvice(adviceResult);
        setChartData(chartDataResult.chartData);
        setCurrentStep('advice');
    } catch (error) {
        handleError(error, 'Advice Generation Failed', 'Failed to generate build mode advice.');
    } finally {
        setIsLoading(false);
    }
  };

  const handleFinalizePlan = async (buildMode: 'in-house' | 'out-sourced') => {
    if (!strategy || !analysis || !selectedOpportunity || !structure || !buildModeAdvice) return;
    try {
      setCurrentStep('finalizing');
      const actionPlanResult = await extractTasksFromStrategy({
        businessStrategy: strategy.businessStrategy,
        buildMode: buildMode,
      });
      setActionPlan(actionPlanResult);
      
      const briefResult = await generateExecutiveBrief({
          opportunityName: selectedOpportunity.opportunityName,
          opportunityDescription: selectedOpportunity.description,
          marketAnalysis: analysis,
          businessStrategy: strategy.businessStrategy,
          actionPlan: {
              criticalPath: actionPlanResult.criticalPath,
              financials: {
                  capex: actionPlanResult.financials.capex,
                  opex: actionPlanResult.financials.opex,
              }
          }
      });
      setExecutiveBrief(briefResult);
      
      localStorage.setItem(`plan_${selectedOpportunity.opportunityName}`, JSON.stringify({
          analysis,
          structure,
          strategy,
          buildModeAdvice,
          actionPlan: actionPlanResult,
          chartData,
          executiveBrief: briefResult,
      }));

      setCurrentStep('done');
    } catch (error) {
        handleError(error, 'Finalization Failed', 'Failed to generate the action plan.');
    }
  }
  
  const handleBackToOpportunities = () => {
    router.push('/opportunities');
  };

  const handlePrint = () => {
    setIsPrinting(true);
    setTimeout(() => {
        window.print();
        setIsPrinting(false);
    }, 100);
  }
  
  const renderInitialState = () => {
    if (!selectedOpportunity) {
      return <OpportunityDashboardSkeleton onBack={handleBackToOpportunities} />;
    }

    return (
       <div className="max-w-4xl mx-auto text-center animate-in fade-in-50 duration-500">
        <h1 className="font-headline text-4xl md:text-5xl font-bold tracking-tighter">
          {selectedOpportunity.opportunityName}
        </h1>
        <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
          {selectedOpportunity.description}
        </p>
        <Card className="mt-12 p-6 bg-card/50">
            <div className="flex flex-col items-center gap-4">
                <div className="flex items-center gap-2 text-primary">
                    <Bot className="h-6 w-6"/>
                    <p className="font-semibold">Ready to build your automated business plan?</p>
                </div>
                <p className="text-sm text-muted-foreground">The AI will guide you through generating a market analysis, strategy, and action plan.</p>
                 <Button size="lg" disabled={isLoading} onClick={handleStartAnalysis}>
                    <Rocket className="mr-2 h-4 w-4"/>
                    {isLoading ? "Analyzing..." : "Start Building Plan"}
                </Button>
            </div>
        </Card>
        <Button variant="ghost" size="sm" onClick={handleBackToOpportunities} className="mt-8">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Opportunities
        </Button>
      </div>
    );
  }

  const renderPipeline = () => {
    const steps = ["Analysis", "Strategy", "Advice", "Finalize"];
    const isFinalizing = currentStep === 'finalizing';
    const stepIndex = currentStep === 'analysis' ? 0 : currentStep === 'strategy' ? 1 : currentStep === 'advice' ? 2 : 3;

    if (currentStep === 'finalizing' || currentStep === 'done') return null;

    return (
        <div className="max-w-4xl mx-auto animate-in fade-in-50 duration-500">
            <div className="mb-8">
                <h1 className="font-headline text-3xl md:text-4xl font-bold tracking-tight text-center">
                    {selectedOpportunity?.opportunityName}
                </h1>
                <StepProgressBar steps={steps} currentStep={stepIndex} />
            </div>

            {currentStep === 'initial' && isLoading && <OpportunityDashboardSkeleton onBack={handleBackToOpportunities} title="Analyzing Market & Structure..." />}
            {currentStep === 'analysis' && <AnalysisStep analysis={analysis} structure={structure} onNext={handleGenerateStrategy} isLoading={isLoading} />}
            {currentStep === 'strategy' && <StrategyStep strategy={strategy} onNext={handleGenerateAdvice} isLoading={isLoading} />}
            {currentStep === 'advice' && buildModeAdvice && (
                <BuildModeSelector
                    advice={buildModeAdvice}
                    onSelectBuildMode={handleFinalizePlan}
                    isFinalizing={isLoading || isFinalizing}
                />
            )}
        </div>
    )
  }

  const renderDashboard = () => {
    if (!selectedOpportunity || !analysis || !structure || !strategy || !actionPlan) return null;

    return (
        <OpportunityDashboard
            opportunity={selectedOpportunity}
            analysis={analysis}
            structure={structure}
            strategy={strategy}
            actionPlan={actionPlan}
            chartData={chartData}
            executiveBrief={executiveBrief}
            onBack={handleBackToOpportunities}
            isPrinting={isPrinting}
        />
    )
  }

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AppHeader>
        {currentStep === 'done' && (
          <Button onClick={handlePrint} variant="outline" size="sm" className="ml-auto print:hidden">
            <Printer className="mr-2 h-4 w-4" />
            Export as Blueprint
          </Button>
        )}
      </AppHeader>
      <main className="flex-1 container mx-auto px-4 py-8">
       {currentStep === 'initial' && !isLoading && renderInitialState()}
       {['initial', 'analysis', 'strategy', 'advice'].includes(currentStep) && renderPipeline()}
       {currentStep === 'finalizing' && <OpportunityDashboardSkeleton onBack={handleBackToOpportunities} title="Finalizing Your Business Plan..." />}
       {currentStep === 'done' && renderDashboard()}
      </main>
    </div>
  );
}
