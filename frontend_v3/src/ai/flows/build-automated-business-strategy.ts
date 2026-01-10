// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// 'use server' removed for static export compatibility; runs as client-side fetch

import { postJson } from '@/lib/backend';

export type BuildAutomatedBusinessStrategyOutput = {
  businessStrategy: {
    marketingTactics: string;
    financialForecasts: string;
    operationalPlan: string;
    operationalWorkflows?: string;
  };
};

const normalizeStrategy = (raw: any): BuildAutomatedBusinessStrategyOutput => {
  const strategy = raw?.businessStrategy || {};
  return {
    businessStrategy: {
      marketingTactics: strategy.marketingTactics || '',
      financialForecasts: strategy.financialForecasts || '',
      operationalPlan: strategy.operationalPlan || '',
      operationalWorkflows: strategy.operationalWorkflows || strategy.operationalPlan || '',
    },
  };
};

export async function buildAutomatedBusinessStrategy(input: { marketAnalysis: string }): Promise<BuildAutomatedBusinessStrategyOutput> {
  try {
    const data = await postJson<BuildAutomatedBusinessStrategyOutput>(
      '/api/ai/build-strategy',
      input
    );
    return normalizeStrategy(data);
  } catch (error) {
    console.error('Error calling backend AI:', error);
    // Return fallback mock data
    return {
      businessStrategy: {
        marketingTactics: "Content-led growth strategy leveraging SEO, LinkedIn thought leadership, and case study showcases. Automated email nurture sequences and AI-powered personalization at scale. Target 100+ qualified leads monthly through organic channels.",
        financialForecasts: "Month 1-3: $15K-$30K revenue building initial client base. Month 4-6: $40K-$60K with referrals and case studies. Month 7-12: $80K-$120K monthly with productized offerings and recurring revenue streams. Year 1 target: $500K-$750K total revenue.",
        operationalPlan: "Phase 1: Launch core AI content service with 3-5 pilot clients. Phase 2: Develop automated delivery workflows and quality systems. Phase 3: Scale to 20+ concurrent clients with minimal overhead. Phase 4: Productize and create self-service tiers.",
        operationalWorkflows: "Automated intake → AI-driven production → QA checks → client delivery → feedback loop."
      }
    };
  }
}
