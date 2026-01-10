import type { IdentifyPromisingOpportunitiesOutput } from '@/ai/flows/identify-promising-opportunities';
import type { AnalyzeMarketOpportunityOutput } from '@/ai/flows/analyze-market-opportunity';
import type { BuildAutomatedBusinessStrategyOutput } from '@/ai/flows/build-automated-business-strategy';
import type { GenerateBusinessStructureOutput } from '@/ai/flows/generate-business-structure';
import type { ExtractTasksFromStrategyOutput } from '@/ai/flows/extract-tasks-from-strategy';
import type { GenerateChartDataOutput } from '@/ai/flows/generate-chart-data';
import type { GenerateExecutiveBriefOutput } from '@/ai/flows/generate-executive-brief';
import { z } from 'zod';


export type Opportunity = IdentifyPromisingOpportunitiesOutput[0] & {
    source?: string;
    sourceId?: string;
    imageUrl?: string;
    tags?: string[];
    metadata?: Record<string, unknown>;
    rationale?: string;
};

export type Analysis = AnalyzeMarketOpportunityOutput;

export type Strategy = BuildAutomatedBusinessStrategyOutput;

export type BusinessStructure = GenerateBusinessStructureOutput;

export type ActionPlan = ExtractTasksFromStrategyOutput;

export type Task = ActionPlan['actionPlan'][0]['tasks'][0];

export type ChartData = GenerateChartDataOutput['chartData'];

export type ExecutiveBrief = GenerateExecutiveBriefOutput & {
    viabilityScore?: number;
    roiPotential?: string;
    timeToBreakeven?: string;
    strategicRecommendation?: string;
    keyStrengths?: string[];
    potentialRisks?: string[];
};

const BuildModeAnalysis = z.object({
    costBenefitAnalysis: z.string(),
    resourceMetrics: z.string(),
    strategicRecommendation: z.string(),
});

const GenerateBuildModeAdviceOutputSchema = z.object({
    inHouse: BuildModeAnalysis,
    outSourced: BuildModeAnalysis,
});
export type BuildModeAdvice = z.infer<typeof GenerateBuildModeAdviceOutputSchema>;
