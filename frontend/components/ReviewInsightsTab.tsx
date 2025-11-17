import { useEffect, useState, useRef } from 'react';
import { apiClient, ReviewAnalysis } from '../lib/api';
import BarChart from './charts/BarChart';
import PieChart from './charts/PieChart';

export default function ReviewInsightsTab() {
  const [data, setData] = useState<ReviewAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    loadData();
    
    // Cleanup: prevent state updates on unmounted component
    return () => {
      isMountedRef.current = false;
    };
  }, [days]);

  const loadData = async () => {
    try {
      if (!isMountedRef.current) return;
      
      setLoading(true);
      setError(null);
      const summary = await apiClient.getReviewSummary(days);
      
      // Only update state if component is still mounted
      if (isMountedRef.current) {
        setData(summary);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError('Failed to load review data');
        console.error(err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-red-500">{error || 'No data available'}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Period selector */}
      <div className="flex justify-end">
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Summary metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Total Reviews</h3>
          <div className="text-3xl font-bold text-gray-900 mt-2">{data.total_reviews}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Reviews with Issues</h3>
          <div className="text-3xl font-bold text-gray-900 mt-2">{data.reviews_with_issues}</div>
          <div className="text-sm text-gray-500 mt-1">
            {data.total_reviews > 0
              ? ((data.reviews_with_issues / data.total_reviews) * 100).toFixed(1)
              : 0}%
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Products Mentioned</h3>
          <div className="text-3xl font-bold text-gray-900 mt-2">{Object.keys(data.products).length}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Issue Types</h3>
          <div className="text-3xl font-bold text-gray-900 mt-2">{Object.keys(data.issues).length}</div>
        </div>
      </div>

      {/* Sentiment breakdown */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Sentiment Breakdown</h3>
        <PieChart
          data={Object.entries(data.sentiments).map(([name, value]) => ({
            name,
            value: value as number,
          }))}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Products with Issues</h3>
          <BarChart
            data={data.top_products_with_issues.slice(0, 10).map((p) => ({
              name: p.product,
              value: p.count,
            }))}
          />
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Trending Quality Concerns</h3>
          <BarChart
            data={data.trending_concerns.slice(0, 10).map((c) => ({
              name: c.issue,
              value: c.count,
            }))}
          />
        </div>
      </div>

      {/* Detailed lists */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Products Mentioned</h3>
          <ul className="space-y-2">
            {data.top_products_with_issues.slice(0, 10).map((product, idx) => (
              <li key={idx} className="flex justify-between items-center">
                <span className="text-gray-700">{product.product}</span>
                <div className="text-right">
                  <div className="font-semibold">{product.count}</div>
                  <div className="text-sm text-gray-500">{product.percentage.toFixed(1)}%</div>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Quality Concerns</h3>
          <ul className="space-y-2">
            {data.trending_concerns.slice(0, 10).map((concern, idx) => (
              <li key={idx} className="flex justify-between items-center">
                <span className="text-gray-700">{concern.issue}</span>
                <div className="text-right">
                  <div className="font-semibold">{concern.count}</div>
                  <div className="text-sm text-gray-500">{concern.percentage.toFixed(1)}%</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

