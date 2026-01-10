import { getJson, postJson } from '@/lib/backend';
import type { Opportunity } from '@/lib/types';

type BizopQuery = {
  source?: string;
  limit?: number;
};

export type BizopOpportunity = Opportunity & {
  source?: string;
  sourceId?: string;
  tags?: string[];
  imageUrl?: string;
  rationale?: string;
  metadata?: Record<string, unknown>;
};

export type BizopRefreshResponse = {
  inserted: number;
  updated: number;
  total: number;
};

export async function fetchBizopOpportunities(query: BizopQuery = {}): Promise<BizopOpportunity[]> {
  const params = new URLSearchParams();
  if (query.source) {
    params.set('source', query.source);
  }
  if (query.limit) {
    params.set('limit', String(query.limit));
  }
  const queryString = params.toString();
  const path = queryString ? `/api/bizop/opportunities?${queryString}` : '/api/bizop/opportunities';
  return getJson<BizopOpportunity[]>(path);
}

export async function fetchBizopSources(): Promise<string[]> {
  return getJson<string[]>('/api/bizop/sources');
}

export async function refreshBizopCatalog(): Promise<BizopRefreshResponse> {
  return postJson<BizopRefreshResponse>('/api/bizop/refresh', {});
}
