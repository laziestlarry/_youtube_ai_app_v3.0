import { getJson } from '@/lib/backend';

export type OutcomeSummary = {
  updated_at: string;
  kpi: {
    updated_at?: string | null;
    summary: {
      total?: number;
      on_track?: number;
      at_risk?: number;
      off_track?: number;
      unknown?: number;
      [key: string]: number | undefined;
    };
  };
  revenue: {
    total: number;
    daily: number;
    last_24h: number;
    last_7d: number;
    last_30d?: number;
    mtd?: number;
    top_sources: Array<{ source: string; amount: number }>;
  };
  pipeline: {
    bizop_total: number;
    workflow_velocity: number;
  };
};

export async function fetchOutcomeSummary(): Promise<OutcomeSummary> {
  return getJson<OutcomeSummary>('/api/outcomes/summary');
}
