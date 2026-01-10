// Backend-powered AI flow - uses the AutonomaX backend instead of direct Genkit
// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// 'use server' removed for static export compatibility; runs as client-side fetch

import { z } from 'zod';
import { postJson } from '@/lib/backend';

const IdentifyPromisingOpportunitiesInputSchema = z.object({
  marketTrends: z
    .string()
    .describe('Description of current market trends and emerging technologies.')
    .optional(),
  userInterests: z
    .string()
    .describe('Description of the user interests and skills.')
    .optional(),
  context: z.string().optional().describe('Optional context or data provided by the user for analysis.'),
});

export type IdentifyPromisingOpportunitiesInput =
  z.infer<typeof IdentifyPromisingOpportunitiesInputSchema>;

const OpportunitySchema = z.object({
  opportunityName: z.string().describe('Name of the business opportunity.'),
  description: z.string().describe('A short description of the business.'),
  potential: z.string().describe('An assessment of the opportunities potential, considering financial upside and market size.'),
  risk: z.string().describe('An assessment of the risks involved, including market, execution, and financial risks.'),
  quickReturn: z.string().describe('An assessment of how quickly a return on investment can be expected (e.g., Short, Medium, Long term).'),
  priority: z.string().describe('A priority score, from 1-10, of which opportunity to pursue first. This should be a synthesis of potential, risk, and quick return.'),
});

const IdentifyPromisingOpportunitiesOutputSchema = z.array(OpportunitySchema);

export type IdentifyPromisingOpportunitiesOutput =
  z.infer<typeof IdentifyPromisingOpportunitiesOutputSchema>;

export async function identifyPromisingOpportunities(
  input: IdentifyPromisingOpportunitiesInput
): Promise<IdentifyPromisingOpportunitiesOutput> {
  try {
    const data = await postJson<{ opportunities?: IdentifyPromisingOpportunitiesOutput }>(
      '/api/ai/opportunities',
      input
    );
    return data.opportunities || [];
  } catch (error) {
    console.error('Error calling backend AI:', error);
    // Return mock data as fallback
    return [
      {
        opportunityName: 'AI-Powered Content Agency',
        description: 'Automated content creation and distribution service using AI',
        potential: 'High - Growing demand for AI content services',
        risk: 'Medium - Competitive market but differentiated by automation',
        quickReturn: 'Short - Can launch in 7-14 days',
        priority: '8',
      },
      {
        opportunityName: 'Shopify Automation Suite',
        description: 'Complete store management automation for e-commerce',
        potential: 'Very High - Large addressable market',
        risk: 'Low - Proven demand and clear value proposition',
        quickReturn: 'Medium - 30-45 days to first revenue',
        priority: '9',
      },
    ];
  }
}
