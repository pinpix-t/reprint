import { useEffect, useState, useRef } from 'react';
import { apiClient, ReviewAnalysis } from '../lib/api';
import { useFilters } from '../contexts/FilterContext';
import GlobalFilters from './GlobalFilters';
import BarChart from './charts/BarChart';
import PieChart from './charts/PieChart';

export default function ReviewInsightsTab() {
  const { filters } = useFilters();
  const [data, setData] = useState<ReviewAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);
  const [investigationResults, setInvestigationResults] = useState<any>(null);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    loadData();
    
    // Cleanup: prevent state updates on unmounted component
    return () => {
      isMountedRef.current = false;
    };
  }, [days, filters]);

  const loadData = async () => {
    try {
      if (!isMountedRef.current) return;
      
      setLoading(true);
      setError(null);
      
      const startDate = filters.startDate || undefined;
      const endDate = filters.endDate || undefined;
      
      const summary = startDate && endDate
        ? await apiClient.getReviewAnalysis(startDate, endDate)
        : await apiClient.getReviewSummary(days);
      
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

  const runInvestigation = async () => {
    try {
      setLoading(true);
      const startDate = filters.startDate || undefined;
      const endDate = filters.endDate || undefined;
      
      // Run investigation based on filters
      const [reprints, reviews] = await Promise.all([
        apiClient.getReprintRecords(
          startDate,
          endDate,
          filters.facility || undefined,
          filters.productType || undefined,
          filters.reasonCategory || undefined,
          filters.shippingCountry || undefined,
          filters.shippingService || undefined,
          100
        ),
        filters.productType
          ? apiClient.getProductQuality(filters.productType, days)
          : Promise.resolve(null),
      ]);
      
      setInvestigationResults({
        reprints: reprints.records || [],
        reviews,
        filters: { ...filters },
      });
    } catch (err) {
      setError('Failed to run investigation');
      console.error(err);
    } finally {
      setLoading(false);
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
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Global Filters Sidebar */}
      <div className="lg:col-span-1">
        <GlobalFilters />
      </div>

      {/* Main Content */}
      <div className="lg:col-span-3 space-y-6">
        {/* Period selector */}
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold">Review Insights & Issue Explorer</h2>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value={1}>Yesterday / Past 24hrs</option>
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

        {/* Investigation Panel */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Investigation Panel</h3>
          <p className="text-sm text-gray-500 mb-4">
            Use filters above to investigate specific products, facilities, or issues. Click "Run Investigation" to analyze.
          </p>
          <button
            onClick={runInvestigation}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 mb-4"
          >
            Run Investigation
          </button>
          
          {investigationResults && (
            <div className="mt-4 space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Investigation Results</h4>
                <p className="text-sm text-gray-600">
                  Filters: {Object.entries(investigationResults.filters)
                    .filter(([_, v]) => v)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(', ') || 'None'}
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Reprints Found: {investigationResults.reprints.length}</h4>
                {investigationResults.reprints.length > 0 && (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 text-sm">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left">Date</th>
                          <th className="px-4 py-2 text-left">Order #</th>
                          <th className="px-4 py-2 text-left">Product</th>
                          <th className="px-4 py-2 text-left">Facility</th>
                          <th className="px-4 py-2 text-left">Reason</th>
                          <th className="px-4 py-2 text-left">Ticket</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {investigationResults.reprints.slice(0, 10).map((record: any, idx: number) => (
                          <tr key={idx}>
                            <td className="px-4 py-2">
                              {record.requested_date ? new Date(record.requested_date).toLocaleDateString() : '-'}
                            </td>
                            <td className="px-4 py-2">{record.order_number || '-'}</td>
                            <td className="px-4 py-2">{record.product_type || '-'}</td>
                            <td className="px-4 py-2">{record.facility || '-'}</td>
                            <td className="px-4 py-2">{record.reprint_reason || '-'}</td>
                            <td className="px-4 py-2">
                              {/* Placeholder for Freshdesk ticket link */}
                              <span className="text-gray-400 text-xs">Link coming soon</span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Quality Score Visualization (Placeholder) */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Quality Risk Score</h3>
          <p className="text-sm text-gray-500 mb-4">
            Quality scores will be calculated based on reprints, Freshdesk tickets, and reviews.
          </p>
          <div className="text-center text-gray-400 py-8">
            Quality Score Calculation Coming Soon
          </div>
        </div>
      </div>
    </div>
  );
}

