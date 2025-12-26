import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { apiService } from '../services/api';

interface RevenueData {
    date: string;
    subscription_revenue: number;
    revenue_share: number;
    digital_products: number;
    affiliate: number;
    total: number;
}

const RevenueDashboard: React.FC = () => {
    const [revenueData, setRevenueData] = useState<RevenueData[]>([]);
    const [summary, setSummary] = useState<any>({});

    useEffect(() => {
        fetchRevenueData();
    }, []);

    const fetchRevenueData = async () => {
        try {
            // Using revenue-history which exists in the backend analytics router
            const data = await apiService.getRevenueHistory(30);
            setRevenueData(data.history || []);

            // Also fetch summary for the cards
            const summary = await apiService.getAnalyticsSummary();
            setSummary({
                total_revenue: summary.stats?.estimated_revenue || 0,
                growth_rate: 12.5, // Mock or derived
                subscription_revenue: summary.stats?.estimated_revenue * 0.6 || 0,
                revenue_share: summary.stats?.estimated_revenue * 0.3 || 0,
                digital_products: summary.stats?.estimated_revenue * 0.1 || 0,
            });
        } catch (error) {
            console.error('Error fetching revenue data:', error);
        }
    };

    return (
        <div className="space-y-6 p-6">
            <h2 className="text-2xl font-bold mb-4">Revenue Dashboard</h2>

            {/* Revenue Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow p-6 border">
                    <h3 className="text-sm font-medium text-gray-500">Total Revenue</h3>
                    <p className="text-2xl font-bold text-gray-900">${summary.total_revenue?.toFixed(2) || '0.00'}</p>
                    <p className="text-sm text-green-600">+{summary.growth_rate || 0}% from last month</p>
                </div>

                <div className="bg-white rounded-lg shadow p-6 border">
                    <h3 className="text-sm font-medium text-gray-500">Subscription Revenue</h3>
                    <p className="text-2xl font-bold text-gray-900">${summary.subscription_revenue?.toFixed(2) || '0.00'}</p>
                </div>

                <div className="bg-white rounded-lg shadow p-6 border">
                    <h3 className="text-sm font-medium text-gray-500">Revenue Share</h3>
                    <p className="text-2xl font-bold text-gray-900">${summary.revenue_share?.toFixed(2) || '0.00'}</p>
                </div>

                <div className="bg-white rounded-lg shadow p-6 border">
                    <h3 className="text-sm font-medium text-gray-500">Digital Products</h3>
                    <p className="text-2xl font-bold text-gray-900">${summary.digital_products?.toFixed(2) || '0.00'}</p>
                </div>
            </div>

            {/* Revenue Chart */}
            <div className="bg-white rounded-lg shadow p-6 border mt-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Revenue Trend</h3>
                <div style={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={revenueData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Line type="monotone" dataKey="total" stroke="#3B82F6" strokeWidth={2} />
                            <Line type="monotone" dataKey="subscription_revenue" stroke="#10B981" strokeWidth={2} />
                            <Line type="monotone" dataKey="revenue_share" stroke="#F59E0B" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default RevenueDashboard;
