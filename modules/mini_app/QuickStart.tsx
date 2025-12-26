import React, { useState, useEffect } from 'react';

interface MoneyIdea {
  title: string;
  category: string;
  expected_views: number;
  estimated_revenue: number;
  cpm_rating: string;
  urgency_score: number;
}

const QuickStart: React.FC = () => {
  const [ideas, setIdeas] = useState<MoneyIdea[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalRevenue, setTotalRevenue] = useState(0);

  const fetchMoneyIdeas = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/money-ideas');
      const data = await response.json();
      setIdeas(data.ideas);
      setTotalRevenue(data.total_revenue_potential);
    } catch (error) {
      console.error('Error fetching ideas:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMoneyIdeas();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🚀 YouTube Income Commander</h1>
      <div style={{ backgroundColor: '#e8f5e8', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2>💰 Revenue Potential: ${totalRevenue.toFixed(2)}</h2>
        <p>Start creating these high-value videos today!</p>
      </div>

      <button 
        onClick={fetchMoneyIdeas}
        disabled={loading}
        style={{
          backgroundColor: '#4CAF50',
          color: 'white',
          padding: '10px 20px',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          marginBottom: '20px'
        }}
      >
        {loading ? 'Generating...' : 'Get New Money-Making Ideas'}
      </button>

      <div>
        {ideas.map((idea, index) => (
          <div key={index} style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '15px',
            marginBottom: '15px',
            backgroundColor: '#f9f9f9'
          }}>
            <h3 style={{ color: '#2c5aa0', marginBottom: '10px' }}>
              {idea.title}
            </h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ backgroundColor: '#ff6b6b', color: 'white', padding: '2px 8px', borderRadius: '12px', fontSize: '12px' }}>
                  HIGH CPM
                </span>
                <span style={{ marginLeft: '10px', color: '#666' }}>
                  Expected Views: {idea.expected_views.toLocaleString()}
                </span>
              </div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#27ae60' }}>
                ${idea.estimated_revenue.toFixed(2)}
              </div>
            </div>
            <div style={{ marginTop: '10px' }}>
              <span style={{ color: '#e74c3c', fontWeight: 'bold' }}>
                Urgency: {idea.urgency_score}/10
              </span>
            </div>
          </div>
        ))}
      </div>

      <div style={{ backgroundColor: '#fff3cd', padding: '15px', borderRadius: '8px', marginTop: '20px' }}>
        <h3>⚡ Quick Action Steps:</h3>
        <ol>
          <li>Pick the highest revenue idea above</li>
          <li>Create a 10-15 minute video</li>
          <li>Upload with optimized title and thumbnail</li>
          <li>Enable monetization immediately</li>
          <li>Add affiliate links in description</li>
        </ol>
      </div>
    </div>
  );
};

export default QuickStart;