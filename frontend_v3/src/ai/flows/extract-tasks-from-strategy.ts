// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// 'use server' removed for static export compatibility; runs as client-side fetch

import { postJson } from '@/lib/backend';

export type ActionPlanTask = {
  id: string;
  title: string;
  description: string;
  priority: 'High' | 'Medium' | 'Low';
  completed: boolean;
  startDate: string;
  endDate: string;
  humanContribution?: string;
};

export type ActionPlanCategory = {
  categoryTitle: string;
  tasks: ActionPlanTask[];
};

export type ActionPlanFinancialItem = {
  item: string;
  amount: string;
  justification: string;
};

export type ActionPlanInvestmentOption = {
  type: string;
  amount: string;
  description: string;
};

export type ActionPlanFinancials = {
  capex: ActionPlanFinancialItem[];
  opex: ActionPlanFinancialItem[];
  investmentOptions: ActionPlanInvestmentOption[];
};

export type ActionPlanCriticalPath = {
  taskTitle: string;
  timeEstimate: string;
};

export type ActionPlanBusinessModelCanvas = {
  keyPartners: string[];
  keyActivities: string[];
  keyResources: string[];
  valuePropositions: string[];
  customerRelationships: string[];
  channels: string[];
  customerSegments: string[];
  costStructure: string[];
  revenueStreams: string[];
};

export type ExtractTasksFromStrategyOutput = {
  actionPlan: ActionPlanCategory[];
  criticalPath: ActionPlanCriticalPath;
  financials: ActionPlanFinancials;
  businessModelCanvas: ActionPlanBusinessModelCanvas;
};

const normalizeActionPlan = (raw: any): ExtractTasksFromStrategyOutput => {
  const rawCategories = Array.isArray(raw?.actionPlan) ? raw.actionPlan : [];
  const now = new Date();

  const actionPlan: ActionPlanCategory[] = rawCategories.map((category: any, categoryIndex: number) => {
    const categoryTitle = category?.categoryTitle || category?.phase || category?.title || `Phase ${categoryIndex + 1}`;
    const rawTasks = Array.isArray(category?.tasks) ? category.tasks : [];

    const tasks = rawTasks.map((task: any, taskIndex: number) => {
      const title = task?.title || task?.task || `Task ${taskIndex + 1}`;
      const description = task?.description || task?.duration || 'Task details pending.';
      const priority = (task?.priority as ActionPlanTask['priority']) || 'Medium';
      const start = new Date(now);
      start.setDate(start.getDate() + categoryIndex + taskIndex);
      const durationDays = Number.parseInt(String(task?.duration || ''), 10);
      const end = new Date(start);
      end.setDate(start.getDate() + (Number.isFinite(durationDays) ? durationDays : 7));

      return {
        id: task?.id || `${categoryIndex}-${taskIndex}`,
        title,
        description,
        priority,
        completed: Boolean(task?.completed),
        startDate: task?.startDate || start.toISOString(),
        endDate: task?.endDate || end.toISOString(),
        humanContribution: task?.humanContribution,
      };
    });

    return {
      categoryTitle,
      tasks,
    };
  });

  const criticalPath: ActionPlanCriticalPath =
    raw?.criticalPath && typeof raw.criticalPath === 'object'
      ? {
        taskTitle: raw.criticalPath.taskTitle || raw.criticalPath.title || 'Critical task',
        timeEstimate: raw.criticalPath.timeEstimate || raw.criticalPath.duration || 'TBD',
      }
      : {
        taskTitle: typeof raw?.criticalPath === 'string' ? raw.criticalPath : 'Critical task',
        timeEstimate: 'TBD',
      };

  const capex = Array.isArray(raw?.financials?.capex)
    ? raw.financials.capex
    : raw?.financials?.capex
      ? [{ item: 'CAPEX', amount: String(raw.financials.capex), justification: 'Provided by model.' }]
      : [];
  const opex = Array.isArray(raw?.financials?.opex)
    ? raw.financials.opex
    : raw?.financials?.opex
      ? [{ item: 'OPEX', amount: String(raw.financials.opex), justification: 'Provided by model.' }]
      : [];
  const investmentOptions = Array.isArray(raw?.financials?.investmentOptions) ? raw.financials.investmentOptions : [];

  const financials: ActionPlanFinancials = {
    capex,
    opex,
    investmentOptions,
  };

  const businessModelCanvas: ActionPlanBusinessModelCanvas = {
    keyPartners: raw?.businessModelCanvas?.keyPartners || [],
    keyActivities: raw?.businessModelCanvas?.keyActivities || [],
    keyResources: raw?.businessModelCanvas?.keyResources || [],
    valuePropositions: raw?.businessModelCanvas?.valuePropositions || [],
    customerRelationships: raw?.businessModelCanvas?.customerRelationships || [],
    channels: raw?.businessModelCanvas?.channels || [],
    customerSegments: raw?.businessModelCanvas?.customerSegments || [],
    costStructure: raw?.businessModelCanvas?.costStructure || [],
    revenueStreams: raw?.businessModelCanvas?.revenueStreams || [],
  };

  return {
    actionPlan,
    criticalPath,
    financials,
    businessModelCanvas,
  };
};

export async function extractTasksFromStrategy(input: { businessStrategy: any; buildMode: string }): Promise<ExtractTasksFromStrategyOutput> {
  try {
    const data = await postJson<ExtractTasksFromStrategyOutput>(
      '/api/ai/extract-tasks',
      input
    );
    return normalizeActionPlan(data);
  } catch (error) {
    console.error('Error calling backend AI:', error);
    // Return fallback mock data
    return normalizeActionPlan({
      actionPlan: [
        {
          phase: "Foundation (Week 1-2)",
          tasks: [
            { task: "Set up AI infrastructure and tooling (ChatGPT API, automation platforms)", duration: "3 days" },
            { task: "Create brand identity and basic website/landing page", duration: "4 days" },
            { task: "Develop initial service packages and pricing", duration: "2 days" }
          ]
        },
        {
          phase: "Launch (Week 3-4)",
          tasks: [
            { task: "Onboard first 3 pilot clients at discounted rates", duration: "7 days" },
            { task: "Build automated content delivery workflows", duration: "5 days" },
            { task: "Create case studies and testimonials", duration: "3 days" }
          ]
        },
        {
          phase: "Scale (Month 2-3)",
          tasks: [
            { task: "Implement automated lead generation system", duration: "10 days" },
            { task: "Scale to 10-15 active clients", duration: "30 days" },
            { task: "Develop self-service onboarding portal", duration: "14 days" }
          ]
        }
      ],
      criticalPath: {
        taskTitle: "AI infrastructure setup → Pilot client onboarding",
        timeEstimate: "90 days to full operation"
      },
      financials: {
        capex: [
          { item: "AI tools", amount: "$2,000", justification: "Core automation and model access." },
          { item: "Website/branding", amount: "$3,000", justification: "Launch-ready brand presence." }
        ],
        opex: [
          { item: "AI API costs", amount: "$500/mo", justification: "Ongoing inference and tools." },
          { item: "Hosting/tools", amount: "$300/mo", justification: "Infrastructure and workflow tooling." }
        ],
        investmentOptions: [
          { type: "Self-funded", amount: "$8,000", description: "Bootstrap with personal capital." },
          { type: "Angel investment", amount: "$25,000", description: "Accelerate growth and hiring." }
        ]
      },
      businessModelCanvas: {
        keyPartners: ["Automation platforms", "AI model providers", "Creative freelancers"],
        keyActivities: ["Content automation", "Client onboarding", "Quality assurance"],
        keyResources: ["AI workflows", "Prompt library", "Delivery pipelines"],
        valuePropositions: ["Fast, affordable content production", "Automation-first delivery"],
        customerRelationships: ["Self-serve onboarding", "Dedicated account support"],
        channels: ["Content marketing", "Referral partnerships", "Outbound sales"],
        customerSegments: ["SMBs", "Creators", "E-commerce brands"],
        costStructure: ["API usage", "Infrastructure", "Marketing"],
        revenueStreams: ["Monthly retainers", "Project-based fees", "Upsells"]
      }
    });
  }
}
