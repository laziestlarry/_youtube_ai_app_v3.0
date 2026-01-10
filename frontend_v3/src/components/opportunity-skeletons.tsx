import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import type { Opportunity } from '@/lib/types';


export const OpportunityListSkeleton = ({title = "Discovering Opportunities..."}: {title?: string}) => (
  <div>
    <h2 className="font-headline text-3xl font-bold tracking-tight mb-8">{title}</h2>
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="border bg-card text-card-foreground rounded-lg shadow-sm">
          <div className="p-6">
            <Skeleton className="h-6 w-3/4 mb-2" />
            <Skeleton className="h-4 w-full mb-4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
          <div className="p-6 pt-0">
             <Skeleton className="h-16 w-full mb-4" />
          </div>
          <div className="flex items-center p-6 pt-0">
            <Skeleton className="h-10 w-28" />
          </div>
        </div>
      ))}
    </div>
  </div>
);

export const OpportunityDashboardSkeleton = ({ onBack, title = "Loading Dashboard..." }: { onBack: () => void, title?: string }) => (
    <div className="animate-pulse">
        <div className="flex items-center gap-4 mb-4">
            <Skeleton className="h-9 w-48" />
        </div>
        <Skeleton className="h-10 w-96 mb-8" />
        
        <div className="text-center">
            <h2 className="font-headline text-2xl font-bold tracking-tight mb-4 text-primary">{title}</h2>
            <p className="text-muted-foreground mb-8">The AI is analyzing the opportunity and generating your business plan...</p>
        </div>

        <div className="space-y-8">
            <div className="grid grid-cols-5 gap-2">
                <Skeleton className="h-10 col-span-1 rounded-md" />
                <Skeleton className="h-10 col-span-1 rounded-md" />
                <Skeleton className="h-10 col-span-1 rounded-md" />
                <Skeleton className="h-10 col-span-1 rounded-md" />
                <Skeleton className="h-10 col-span-1 rounded-md" />
            </div>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                <Skeleton className="h-32 rounded-lg" />
                <Skeleton className="h-32 rounded-lg" />
                <Skeleton className="h-32 rounded-lg" />
            </div>
            <Skeleton className="h-64 w-full rounded-lg" />
        </div>
    </div>
);
