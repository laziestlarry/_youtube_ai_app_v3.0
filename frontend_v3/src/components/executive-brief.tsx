'use client';

import type { ExecutiveBrief } from '@/lib/types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, Clock, TrendingUp, XCircle, GaugeCircle } from 'lucide-react';
import { PolarGrid, RadialBar, RadialBarChart } from 'recharts';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';


const BriefGadget = ({ title, value, icon }: { title: string; value: React.ReactNode; icon: React.ReactNode }) => (
    <div className="flex flex-col items-center justify-center p-4 text-center rounded-lg bg-card/50">
        <div className="flex items-center gap-2 mb-2 text-muted-foreground">
            {icon}
            <h4 className="font-semibold text-sm">{title}</h4>
        </div>
        <div className="text-2xl font-bold text-foreground flex items-center justify-center h-24">{value}</div>
    </div>
);

const ViabilityGauge = ({ score }: { score: number }) => {
    const chartData = [{ name: 'score', value: score * 10, fill: 'hsl(var(--primary))' }];
    
    return (
        <div className="relative w-24 h-24 flex items-center justify-center">
            <ChartContainer
                config={{
                    score: {
                        label: 'Score',
                        color: 'hsl(var(--chart-1))',
                    },
                }}
                className="mx-auto aspect-square h-full w-full"
            >
                <RadialBarChart
                    data={chartData}
                    startAngle={-210}
                    endAngle={30}
                    innerRadius={80}
                    outerRadius={100}
                    barSize={10}
                >
                    <PolarGrid
                        gridType="circle"
                        radialLines={false}
                        stroke="none"
                        className="fill-muted"
                    />
                    <RadialBar dataKey="value" background cornerRadius={5} />
                </RadialBarChart>
            </ChartContainer>
             <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-2xl font-bold text-foreground">
                    {score.toFixed(1)}
                </span>
                <span className="text-xs text-muted-foreground -mt-1">/ 10</span>
            </div>
        </div>
    );
};


export default function ExecutiveBriefDisplay({ brief }: { brief: ExecutiveBrief }) {
    const viabilityScore = brief.viabilityScore ?? 7.5;
    const roiPotential = brief.roiPotential ?? 'High';
    const timeToBreakeven = brief.timeToBreakeven ?? brief.keyMetrics?.breakEvenPoint ?? 'N/A';
    const strategicRecommendation =
        brief.strategicRecommendation ??
        (brief.executiveSummary ? `${brief.executiveSummary.split('. ')[0]}.` : 'Proceed with cautious optimism.');
    const keyStrengths = (brief.keyStrengths ??
        [
            brief.keyMetrics?.timeToMarket,
            brief.keyMetrics?.yearOneRevenue,
            brief.keyMetrics?.initialInvestment,
        ].filter((item): item is string => Boolean(item))) as string[];
    const potentialRisks = brief.potentialRisks ??
        (brief.riskAssessment ? [brief.riskAssessment] : ['Risk assessment unavailable.']);

    return (
        <Card className="mb-8 border-2 border-primary/50 shadow-lg">
            <CardHeader>
                <CardTitle className="font-headline text-2xl">Executive Brief</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <BriefGadget 
                        title="Viability Score"
                        icon={<GaugeCircle className="h-4 w-4" />}
                        value={<ViabilityGauge score={viabilityScore} />} 
                    />
                    <BriefGadget 
                        title="ROI Potential" 
                        icon={<TrendingUp className="h-4 w-4" />}
                        value={<Badge variant={roiPotential === 'High' ? 'default' : 'secondary'} className="text-xl px-4 py-1">{roiPotential}</Badge>} 
                    />
                    <BriefGadget 
                        title="Time to Breakeven" 
                        icon={<Clock className="h-4 w-4" />}
                        value={timeToBreakeven} 
                    />
                     <div className="col-span-2 md:col-span-1 flex flex-col items-center justify-center p-4 text-center rounded-lg bg-card/50">
                        <p className="text-sm font-semibold text-center">{strategicRecommendation}</p>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-base text-green-500">
                                <CheckCircle className="h-5 w-5" />
                                Key Strengths
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                                {keyStrengths.map((item, index) => <li key={index}>{item}</li>)}
                            </ul>
                        </CardContent>
                    </Card>
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2 text-base text-destructive">
                                <XCircle className="h-5 w-5" />
                                Potential Risks
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                             <ul className="list-disc list-inside space-y-2 text-muted-foreground">
                                {potentialRisks.map((item, index) => <li key={index}>{item}</li>)}
                            </ul>
                        </CardContent>
                    </Card>
                </div>
            </CardContent>
        </Card>
    )
}
