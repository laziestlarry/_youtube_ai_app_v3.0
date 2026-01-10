'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/use-toast';
import { identifyPromisingOpportunities } from '@/ai/flows/identify-promising-opportunities';
import type { IdentifyPromisingOpportunitiesInput } from '@/ai/flows/identify-promising-opportunities';
import AppHeader from '@/components/app-header';
import OpportunityForm from '@/components/opportunity-form';
import { OpportunityListSkeleton } from '@/components/opportunity-skeletons';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from '@/components/ui/carousel';
import { Lightbulb, BrainCircuit, Rocket } from 'lucide-react';

const featureHighlights = [
    {
        icon: <Lightbulb className="h-10 w-10 text-accent" />,
        title: "Analyze & Discover",
        description: "Upload any document—business plans, meeting notes, or raw ideas. Our AI sifts through the noise to identify high-potential, actionable business opportunities hidden in your data."
    },
    {
        icon: <BrainCircuit className="h-10 w-10 text-accent" />,
        title: "Strategize & Plan",
        description: "Once an opportunity is selected, the AI generates a complete strategic blueprint, including market analysis, an automated organizational structure, and a step-by-step action plan."
    },
    {
        icon: <Rocket className="h-10 w-10 text-accent" />,
        title: "Build & Execute",
        description: "Engage the 'Genesis Protocol' and watch as your AI-Corp executes the plan. A command-line interface shows your new business being 'built' in real-time."
    }
]

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();
  const router = useRouter();

  const handleSubmit = async (data: IdentifyPromisingOpportunitiesInput) => {
    setIsLoading(true);
    try {
      const result = await identifyPromisingOpportunities(data);
      if (result && result.length > 0) {
        localStorage.setItem('discoveredOpportunities', JSON.stringify(result));
        router.push('/opportunities');
      } else {
        toast({
          variant: 'destructive',
          title: 'Analysis Failed',
          description: 'The AI could not identify any opportunities from the data provided.',
        });
        setIsLoading(false);
      }
    } catch (error) {
      console.error(error);
      toast({
        variant: 'destructive',
        title: 'An Error Occurred',
        description: 'Failed to analyze the provided data. Please try again.',
      });
      setIsLoading(false);
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return <OpportunityListSkeleton />;
    }

    return (
       <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12 animate-in fade-in-50 duration-500">
          <h1 className="font-headline text-4xl md:text-5xl font-bold tracking-tighter">
            Transform Your Knowledge into an AI-Powered Enterprise
          </h1>
          <p className="text-muted-foreground mt-4 max-w-2xl mx-auto">
            From raw text to a fully automated business plan. BizOp Navigator analyzes your ideas and builds a strategic blueprint for your next venture.
          </p>
        </div>

        <Carousel
            opts={{
                align: "start",
                loop: true,
            }}
            className="w-full max-w-4xl mx-auto mb-12"
        >
            <CarouselContent>
                {featureHighlights.map((feature, index) => (
                    <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/3">
                         <div className="p-1 h-full">
                            <Card className="flex flex-col h-full text-center items-center">
                                <CardHeader>
                                    {feature.icon}
                                    <CardTitle className="font-headline mt-2">{feature.title}</CardTitle>
                                </CardHeader>
                                <CardContent className="flex-grow">
                                    <p className="text-sm text-muted-foreground">{feature.description}</p>
                                </CardContent>
                            </Card>
                        </div>
                    </CarouselItem>
                ))}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
        </Carousel>

        <OpportunityForm onSubmit={handleSubmit} isSubmitting={isLoading} />
      </div>
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <AppHeader />
      <main className="flex-1 container mx-auto px-4 py-8">
        {renderContent()}
      </main>
    </div>
  );
}
