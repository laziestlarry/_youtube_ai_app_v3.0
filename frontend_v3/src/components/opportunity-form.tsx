'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import type { IdentifyPromisingOpportunitiesInput } from '@/ai/flows/identify-promising-opportunities';

const formSchema = z.object({
  userInterests: z.string().optional(),
  marketTrends: z.string().optional(),
  context: z.string().optional(),
}).refine(data => !!data.userInterests || !!data.marketTrends || !!data.context, {
  message: "Please fill out at least one field to get started.",
  path: ["context"], // Show error under the main field
});


interface OpportunityFormProps {
  onSubmit: (data: IdentifyPromisingOpportunitiesInput) => void;
  isSubmitting: boolean;
}

export default function OpportunityForm({ onSubmit, isSubmitting }: OpportunityFormProps) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      userInterests: '',
      marketTrends: '',
      context: '',
    },
  });

  return (
    <Card className="shadow-lg">
      <CardHeader>
        <CardTitle className="font-headline text-2xl">Analysis Agent</CardTitle>
        <CardDescription>
          Provide context for the AI to analyze. The more data you provide, the better the results. At least one field is required.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="context"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-base font-semibold">Paste Your Document or Data Here</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Paste any relevant data, documents, articles, or thoughts you want the AI to analyze to discover business opportunities..."
                      className="resize-y min-h-[250px] font-mono text-xs"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="userInterests"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-base">Your Interests & Skills (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="e.g., 'Passionate about sustainable fashion, skilled in digital marketing and graphic design...'"
                      className="resize-y min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="marketTrends"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-base">Observed Market Trends (Optional)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="e.g., 'Growing demand for personalized pet products, rise of AI-powered productivity tools...'"
                      className="resize-y min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <Button type="submit" disabled={isSubmitting} size="lg" className="w-full">
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing & Discovering Opportunities...
                </>
              ) : (
                'Analyze and Discover'
              )}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
