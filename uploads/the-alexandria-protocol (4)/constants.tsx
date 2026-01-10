
import { GenesisEntry, FileStatus, PotentialUse, Proposition, GraphNode, GraphLink, RiskLevel, Funder } from './types';

export const POTENTIAL_FUNDERS: Funder[] = [
  { id: 'v1', name: 'Aetheris Ventures', focus: ['AI Architecture', 'SaaS'], tier: 'Seed', matchScore: 98 },
  { id: 'v2', name: 'Stonebridge Capital', focus: ['Supply Chain', 'Retail Tech'], tier: 'Series A', matchScore: 85 },
  { id: 'v3', name: 'Nova Alpha Partners', focus: ['E-commerce', 'Automation'], tier: 'Seed', matchScore: 92 },
  { id: 'v4', name: 'Blue Chip Logic', focus: ['Enterprise AI', 'Data Science'], tier: 'Enterprise', matchScore: 78 }
];

export const INITIAL_GENESIS_LOG: GenesisEntry[] = [
  {
    id: 'f1',
    name: 'autonoma_x_blueprint.pdf',
    type: 'PDF',
    size: '1.2 MB',
    date: '2025-03-20',
    status: FileStatus.ANALYZED,
    tags: ['ai-engine', 'automation', 'revenue-systems', 'architecture'],
    collection: 'Autonomous Income Systems',
    copyright: 'Proprietary',
    potentialUse: PotentialUse.ACTION,
    description: 'Detailed blueprint for Autonoma-X, an autonomous AI-driven income engine.',
    confidenceScore: 98,
    contentSnippet: 'ABSTRACT: The Autonoma-X framework defines a set of recursive AI agents capable of autonomous revenue generation through arbitrage and digital product management...',
    riskLevel: RiskLevel.LOW
  },
  {
    id: 'f2',
    name: 'retail_predictive_models.zip',
    type: 'Archive',
    size: '45.8 MB',
    date: '2025-01-15',
    status: FileStatus.CATALOGED,
    tags: ['python', 'ml', 'retail', 'forecasting'],
    collection: 'Data Science Models',
    copyright: 'Creative Commons',
    potentialUse: PotentialUse.DIRECT_USE,
    description: 'Predictive analytics modules for demand forecasting and inventory optimization.',
    confidenceScore: 85,
    contentSnippet: '[ARCHIVE CONTENT]: \n- inventory_forecast.py\n- sales_transformer_v2.bin\n- data_cleaning_pipeline.sh\n- readme.md',
    riskLevel: RiskLevel.MEDIUM
  },
  {
    id: 'f3',
    name: 'zen_ui_kit_calm.fig',
    type: 'FIGMA',
    size: '12.4 MB',
    date: '2024-11-30',
    status: FileStatus.CATALOGED,
    tags: ['ui-ux', 'figma', 'design-system', 'meditation'],
    collection: 'Creative Assets 2024',
    copyright: 'Public Domain',
    potentialUse: PotentialUse.INSPIRATION,
    description: 'High-fidelity UI kit for meditation and wellness mobile applications.',
    confidenceScore: 92,
    previewUrl: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=400&h=300',
    riskLevel: RiskLevel.LOW
  },
  {
    id: 'f4',
    name: 'shopify_integration_guide.txt',
    type: 'TXT',
    size: '12 KB',
    date: '2025-02-10',
    status: FileStatus.CATALOGED,
    tags: ['shopify', 'ecommerce', 'api', 'automation'],
    collection: 'Platform Integration Guides',
    copyright: 'Proprietary',
    potentialUse: PotentialUse.LEARNING,
    description: 'Documentation for bridging AI bots with Shopify admin APIs.',
    confidenceScore: 78,
    contentSnippet: '1. API KEY GENERATION: Navigate to Shopify Admin > Apps > App and sales channel settings > Develop apps...',
    riskLevel: RiskLevel.LOW
  },
  {
    id: 'f5',
    name: 'market_signals_q1_2025.csv',
    type: 'CSV',
    size: '2.5 MB',
    date: '2025-03-01',
    status: FileStatus.CATALOGED,
    tags: ['market-data', 'trends', 'csv', 'analysis'],
    collection: 'Intelligence Reports',
    copyright: 'Unknown',
    potentialUse: PotentialUse.ACTION,
    description: 'Raw data of market signals and consumer behavior shifts in Q1 2025.',
    confidenceScore: 88,
    contentSnippet: 'timestamp,sector,sentiment,volatility\n2025-01-01T00:00:00Z,tech,0.85,0.12\n2025-01-01T01:00:00Z,retail,0.62,0.45...',
    riskLevel: RiskLevel.HIGH
  }
];

export const INITIAL_PROPOSITIONS: Proposition[] = [
  {
    id: 'p1',
    type: 'Consultancy',
    title: 'Enterprise Autonomous Revenue Infrastructure',
    targetAudience: 'Mid-sized e-commerce retailers',
    problem: 'Manual product launches and inventory management causing high operational overhead.',
    solution: 'Implementation of the Autonoma-X architecture integrated with real-time predictive models.',
    deliverables: ['Custom ML Pipeline', 'Automated Campaign Orchestrator', 'Executive Dashboard'],
    pricing: '$15k - $50k',
    estimatedROI: '300% YoY',
    feasibility: 85,
    startDate: '2025-04-01',
    endDate: '2025-07-01',
    potentialFunders: ['v1', 'v4']
  },
  {
    id: 'p2',
    type: 'Freelance',
    title: 'Predictive Inventory Optimization',
    targetAudience: 'Shopify Store Owners',
    problem: 'Small retailers struggling with overstocking and cash flow tied up in inventory.',
    solution: 'Modular implementation of demand forecasting scripts from the archive.',
    deliverables: ['Inventory Prediction Script', 'Optimization Report', 'ERP Integration'],
    pricing: '$2,500',
    estimatedROI: '20% Cash Recovery',
    feasibility: 95,
    startDate: '2025-03-25',
    endDate: '2025-04-15',
    potentialFunders: ['v2', 'v3']
  },
  {
    id: 'p3',
    type: 'Digital Product',
    title: 'CalmCommerce Wellness Bundle',
    targetAudience: 'Wellness entrepreneurs',
    problem: 'High barrier to entry for professional wellness-oriented online stores.',
    solution: 'Pre-packaged Shopify theme bundle using the Zen UI Kit and integration logic.',
    deliverables: ['Shopify Theme', 'Landing Templates', 'Marketing Guide'],
    pricing: '$299',
    estimatedROI: 'Low Barrier Entry',
    feasibility: 90,
    startDate: '2025-05-01',
    endDate: '2025-06-01',
    potentialFunders: ['v3']
  }
];

export const GRAPH_DATA = {
  nodes: [
    { id: 'Autonoma-X', label: 'Autonoma-X', type: 'concept' },
    { id: 'f1', label: 'autonoma_x_blueprint.pdf', type: 'file' },
    { id: 'f4', label: 'shopify_integration_guide.txt', type: 'file' },
    { id: 'f2', label: 'retail_predictive_models.zip', type: 'file' },
    { id: 'Ecommerce', label: 'Ecommerce', type: 'tag' },
    { id: 'Revenue-Systems', label: 'Revenue Systems', type: 'collection' },
    { id: 'Data-Science-Models', label: 'Data Science Models', type: 'collection' },
    { id: 'Autonomous-Income-Systems', label: 'Autonomous Income Systems', type: 'collection' }
  ] as GraphNode[],
  links: [
    { source: 'f1', target: 'Autonoma-X', relation: 'defines' },
    { source: 'f4', target: 'Autonoma-X', relation: 'is-a-component-of' },
    { source: 'f2', target: 'Autonoma-X', relation: 'prerequisite-for' },
    { source: 'f4', target: 'Ecommerce', relation: 'shares-tag' },
    { source: 'f1', target: 'Revenue-Systems', relation: 'belongs-to-collection' },
    { source: 'f2', target: 'Data-Science-Models', relation: 'belongs-to-collection' },
    { source: 'f1', target: 'Autonomous-Income-Systems', relation: 'belongs-to-collection' }
  ] as GraphLink[]
};
