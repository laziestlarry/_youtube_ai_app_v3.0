// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// 'use server' removed for static export compatibility; runs as client-side fetch

import { postJson } from '@/lib/backend';

export type GenerateBusinessStructureOutput = {
  commander?: string;
  aiCore: string;
  operations: string;
  sales: string;
  okrs?: Array<{
    objective: string;
    keyResults: string[];
  }>;
  advisoryCouncil?: Array<{
    role: string;
    description: string;
  }>;
  cLevelBoard?: Array<{
    role: string;
    description: string;
  }>;
  projectManagementFramework?: {
    methodology: string;
    phases: Array<{
      phaseName: string;
      description: string;
      keyActivities: string[];
    }>;
  };
  departments?: Array<{
    name: string;
    function: string;
    aiIntegration: string;
    kpis: Array<{
      kpi: string;
      target: string;
    }>;
    staff: Array<{
      role: string;
      persona: string;
    }>;
  }>;
};

export async function generateBusinessStructure(input: { opportunityName: string; opportunityDescription: string }): Promise<GenerateBusinessStructureOutput> {
  try {
    return await postJson<GenerateBusinessStructureOutput>('/api/ai/generate-structure', input);
  } catch (error) {
    console.error('Error calling backend AI:', error);
    // Return fallback mock data
    return {
      commander: "Multi-layered executive oversight combining strategic planning with AI-driven decision automation.",
      aiCore: "Centralized AI orchestration layer powered by GPT-4 and custom automation workflows. Handles content generation, client communication, and quality assurance with 95% automation rate.",
      operations: "Lean operational structure with automated project management, delivery pipelines, and quality control systems. Minimal human intervention required for routine tasks.",
      sales: "Automated lead generation through SEO-optimized content and social proof. Self-service onboarding with AI-powered sales qualification and proposal generation.",
      okrs: [
        {
          objective: "Launch and validate the AI-driven service offering",
          keyResults: ["Ship MVP in 14 days", "Onboard 3 pilot customers", "Achieve 80% task automation"]
        }
      ],
      advisoryCouncil: [
        {
          role: "AI Strategy Advisor",
          description: "Guides model selection, automation priorities, and scaling strategy."
        }
      ],
      cLevelBoard: [
        {
          role: "Chief Operating Officer",
          description: "Oversees workflow execution, QA, and delivery efficiency."
        }
      ],
      projectManagementFramework: {
        methodology: "Agile, 2-week sprints with weekly reviews",
        phases: [
          {
            phaseName: "Foundation",
            description: "Set up tooling, automation workflows, and brand assets.",
            keyActivities: ["Tooling setup", "Brand identity", "Initial SOPs"]
          }
        ]
      },
      departments: [
        {
          name: "Strategy & Innovation",
          function: "Market positioning, pricing, and growth planning.",
          aiIntegration: "AI-assisted research and competitive analysis.",
          kpis: [
            { kpi: "Launch readiness", target: "2 weeks" },
            { kpi: "Market validation", target: "3 pilot clients" }
          ],
          staff: [
            { role: "Growth Strategist AI", persona: "Data-driven market optimizer" }
          ]
        }
      ]
    };
  }
}
