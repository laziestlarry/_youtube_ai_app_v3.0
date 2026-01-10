import { getJson } from '@/lib/backend';

export type KPIStatus = 'on_track' | 'at_risk' | 'off_track' | 'unknown';

export type KPIRecord = {
  id: string;
  name: string;
  category: string;
  target: number;
  unit: string;
  direction: 'up' | 'down';
  owner?: string;
  source?: string;
  actual?: number | null;
  actual_note?: string | null;
  actual_updated_at?: string | null;
  status: KPIStatus;
  status_label: string;
};

export type KPISummary = {
  total: number;
  on_track: number;
  at_risk: number;
  off_track: number;
  unknown: number;
};

export type KPIResponse = {
  updated_at?: string;
  kpis: KPIRecord[];
  summary: KPISummary;
};

export async function fetchKpiTargets(): Promise<KPIResponse> {
  return getJson<KPIResponse>('/api/kpi/targets');
}
