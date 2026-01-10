'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Building, Zap, Briefcase, Clock, Users, Loader2 } from 'lucide-react';
import type { BuildModeAdvice } from '@/lib/types';

interface BuildModeSelectorProps {
    advice: BuildModeAdvice;
    onSelectBuildMode: (buildMode: 'in-house' | 'out-sourced') => void;
    isFinalizing: boolean;
}

const AdviceCard = ({ title, icon, analysis, onSelect, onSelectVariant, isFinalizing, isSelected }: {
    title: string;
    icon: React.ReactNode;
    analysis: BuildModeAdvice['inHouse'];
    onSelect: () => void;
    onSelectVariant: 'default' | 'secondary';
    isFinalizing: boolean;
    isSelected: boolean;

}) => (
    <Card className="flex flex-col text-center p-6 hover:border-primary transition-colors duration-200">
        <div className="flex flex-col items-center">
            {icon}
            <h3 className="font-bold text-2xl mt-4 mb-2">{title}</h3>
        </div>
        <CardContent className="space-y-4 text-left flex-grow">
            <div>
                <h4 className="font-semibold text-lg mb-2">Cost-Benefit Analysis</h4>
                <p className="text-sm text-muted-foreground">{analysis.costBenefitAnalysis}</p>
            </div>
             <div>
                <h4 className="font-semibold text-lg mb-2">Resource Metrics</h4>
                <p className="text-sm text-muted-foreground">{analysis.resourceMetrics}</p>
            </div>
            <div>
                <h4 className="font-semibold text-lg mb-2">Strategic Recommendation</h4>
                <p className="text-sm text-muted-foreground">{analysis.strategicRecommendation}</p>
            </div>
        </CardContent>
        <Button className="w-full mt-auto" onClick={onSelect} variant={onSelectVariant} disabled={isFinalizing}>
           {isFinalizing && isSelected ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Finalizing...
                </>
              ) : (
                `Select ${title}`
              )}
        </Button>
    </Card>
);


export default function BuildModeSelector({ advice, onSelectBuildMode, isFinalizing }: BuildModeSelectorProps) {
    const [selectedMode, setSelectedMode] = useState<'in-house' | 'out-sourced' | null>(null);

    const handleSelect = (mode: 'in-house' | 'out-sourced') => {
        setSelectedMode(mode);
        onSelectBuildMode(mode);
    }
    
    return (
        <Card className="mt-6 border-primary border-2">
            <CardHeader className="text-center">
                <CardTitle className="font-headline text-3xl">Finalize Your Strategy</CardTitle>
                <CardDescription>
                    The AI has analyzed your business plan. Now, choose the best way to build it.
                </CardDescription>
            </CardHeader>
            <CardContent>
                 <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                    <AdviceCard 
                        title="In-House"
                        icon={<Building className="h-12 w-12 text-primary"/>}
                        analysis={advice.inHouse}
                        onSelect={() => handleSelect('in-house')}
                        onSelectVariant="default"
                        isFinalizing={isFinalizing}
                        isSelected={selectedMode === 'in-house'}
                    />
                    <AdviceCard 
                        title="Out-Sourced"
                        icon={<Zap className="h-12 w-12 text-accent"/>}
                        analysis={advice.outSourced}
                        onSelect={() => handleSelect('out-sourced')}
                        onSelectVariant="secondary"
                        isFinalizing={isFinalizing}
                        isSelected={selectedMode === 'out-sourced'}
                    />
                </div>
            </CardContent>
        </Card>
    );
}
