import type { Opportunity } from '@/lib/types';

export type RankedOpportunity = Opportunity & {
  rank: number;
  rationale: string;
};

export async function rankBusinessOpportunities(input: {
  opportunities: Opportunity[];
  focus: string;
}): Promise<RankedOpportunity[] | null> {
  const { opportunities, focus } = input;
  if (!opportunities?.length) return null;

  const scored = opportunities.map((opportunity, index) => {
    const priorityScore = Number.parseInt(opportunity.priority ?? '', 10);
    return {
      opportunity,
      priorityScore: Number.isFinite(priorityScore) ? priorityScore : 0,
      index,
    };
  });

  scored.sort((a, b) => {
    if (b.priorityScore !== a.priorityScore) {
      return b.priorityScore - a.priorityScore;
    }
    return a.index - b.index;
  });

  return scored.map(({ opportunity }, idx) => ({
    ...opportunity,
    rank: idx + 1,
    rationale: `Ranked by priority (${opportunity.priority ?? 'N/A'}) with focus: ${focus}`,
  }));
}
