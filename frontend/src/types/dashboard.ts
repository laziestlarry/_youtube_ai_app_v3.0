export interface ChannelStats {
  subscriber_count: number;
  view_count: number;
  video_count: number;
  estimated_revenue: number;
}

export interface RevenueForecast {
  projected_revenue: number;
  confidence: 'low' | 'medium' | 'high';
}

export interface AnalyticsSummary {
  stats: ChannelStats;
  forecast: RevenueForecast;
  recent_videos: VideoAnalytics[];
}

export interface VideoAnalytics {
  id?: number;
  video_id: string;
  channel_id: string;
  title: string;
  views: number;
  likes: number;
  comments: number;
  revenue: number;
  upload_date: string;
  fetched_at?: string;
}

export interface SystemHealth {
  status: 'healthy' | 'warning' | 'error';
  uptime: number;
  memory: number;
  cpu: number;
  lastCheck: string;
}

export interface AIModel {
  name: string;
  status: 'active' | 'training' | 'inactive';
  accuracy: number;
  lastTrained: string;
  type: 'content' | 'thumbnail' | 'title' | 'description';
}

export interface EarningsData {
  daily: number;
  weekly: number;
  monthly: number;
  yearly: number;
  sources: {
    ads: number;
    sponsorships: number;
    merchandise: number;
    memberships: number;
  };
}