// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// 'use server' removed for static export compatibility; runs as client-side fetch

import { postJson } from '@/lib/backend';

export type GenerateBuildModeAdviceOutput = {
  inHouse: {
    costBenefitAnalysis: string;
    resourceMetrics: string;
    strategicRecommendation: string;
  };
  outSourced: {
    costBenefitAnalysis: string;
    resourceMetrics: string;
    strategicRecommendation: string;
  };
};

export async function generateBuildModeAdvice(input: { businessStrategy: any }): Promise<GenerateBuildModeAdviceOutput> {
  try {
    return await postJson<GenerateBuildModeAdviceOutput>(
      '/api/ai/build-mode-advice',
      input
    );
  } catch (error) {
    console.error('Error calling backend AI:', error);
    // Return fallback mock data
    return {
      inHouse: {
        costBenefitAnalysis: "Initial investment: $5K-$10K for AI tools and infrastructure. Monthly operating costs: $500-$1K. Break-even at 2-3 clients. Higher profit margins (70-80%) long-term.",
        resourceMetrics: "Time to launch: 7-14 days. Required skills: AI prompt engineering, basic automation, client management. Learning curve: 2-4 weeks to proficiency.",
        strategicRecommendation: "Recommended for founders with technical aptitude who want maximum control and profit margins. Best for building sustainable, scalable business with compounding advantages."
      },
      outSourced: {
        costBenefitAnalysis: "Initial investment: $15K-$25K for agency partnerships and setup. Monthly costs: $2K-$5K for outsourced delivery. Break-even at 5-7 clients. Lower margins (40-50%) but faster scaling.",
        resourceMetrics: "Time to launch: 3-7 days. Required skills: Sales, project management, vendor coordination. Minimal technical learning required.",
        strategicRecommendation: "Recommended for founders prioritizing speed to market and focusing on sales/client acquisition. Best for testing market fit quickly before building in-house capabilities."
      }
    };
  }
}
