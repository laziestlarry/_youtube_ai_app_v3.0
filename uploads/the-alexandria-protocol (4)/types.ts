
export enum FileStatus {
  UNPROCESSED = 'Unprocessed',
  CATALOGED = 'Cataloged',
  ANALYZED = 'Analyzed',
  MONETIZED = 'Monetized',
  TRIAGE = 'In Triage'
}

export enum PotentialUse {
  INSPIRATION = 'Inspiration',
  DIRECT_USE = 'Direct Use',
  LEARNING = 'Learning Resource',
  ACTION = 'Action Basis'
}

export enum RiskLevel {
  LOW = 'Low',
  MEDIUM = 'Medium',
  HIGH = 'High'
}

// Added GenesisEntry interface to support archival data management
export interface GenesisEntry {
  id: string;
  name: string;
  type: string;
  size: string;
  date: string;
  status: FileStatus;
  tags: string[];
  collection: string;
  copyright: string;
  potentialUse: PotentialUse;
  description: string;
  confidenceScore: number;
  contentSnippet?: string;
  riskLevel: RiskLevel;
  previewUrl?: string;
}

export interface Funder {
  id: string;
  name: string;
  focus: string[];
  tier: 'Seed' | 'Series A' | 'Enterprise';
  matchScore: number;
}

export interface Proposition {
  id: string;
  type: 'Consultancy' | 'Freelance' | 'Digital Product';
  title: string;
  problem: string;
  solution: string;
  targetAudience: string;
  deliverables: string[];
  pricing: string;
  estimatedROI: string;
  feasibility: number; // 0-100
  startDate: string;
  endDate: string;
  potentialFunders?: string[]; // IDs of funders
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'file' | 'collection' | 'tag' | 'concept';
  metadata?: any;
}

export interface GraphLink {
  source: string;
  target: string;
  relation: string;
}
