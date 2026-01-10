// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// Backend-powered AI flow - uses the AutonomaX backend Chimera Engine
// 'use server' removed for static export compatibility; runs as client-side fetch

import { postJson } from '@/lib/backend';

export type GenerateChartDataOutput = {
  chartData: Array<{
    month: string;
    revenue: number;
  }>;
};

const normalizeChartData = (raw: any): GenerateChartDataOutput => {
  if (Array.isArray(raw?.chartData)) {
    return { chartData: raw.chartData };
  }

  if (raw?.chartData?.labels && raw?.chartData?.datasets?.length) {
    const labels: string[] = raw.chartData.labels;
    const dataset = raw.chartData.datasets.find((item: any) => /revenue/i.test(item.label)) || raw.chartData.datasets[0];
    const data: number[] = dataset?.data || [];
    return {
      chartData: labels.map((label, index) => ({
        month: label,
        revenue: Number(data[index] ?? 0),
      })),
    };
  }

  return { chartData: [] };
};

export async function generateChartData(input: { financialForecasts: string }): Promise<GenerateChartDataOutput> {
  try {
    const data = await postJson<GenerateChartDataOutput>(
      '/api/ai/generate-chart-data',
      input
    );
    return normalizeChartData(data);
  } catch (error) {
    console.error('Error calling backend AI:', error);
    // Return fallback mock data
    return {
      chartData: [
        { month: "Month 1", revenue: 15000 },
        { month: "Month 2", revenue: 22000 },
        { month: "Month 3", revenue: 30000 },
        { month: "Month 4", revenue: 45000 },
        { month: "Month 5", revenue: 55000 },
        { month: "Month 6", revenue: 65000 },
        { month: "Month 7", revenue: 80000 },
        { month: "Month 8", revenue: 95000 },
        { month: "Month 9", revenue: 110000 },
        { month: "Month 10", revenue: 120000 },
        { month: "Month 11", revenue: 130000 },
        { month: "Month 12", revenue: 140000 }
      ]
    };
  }
}
