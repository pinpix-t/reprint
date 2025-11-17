import { useEffect, useState } from 'react';
import { apiClient, OverviewData } from '../lib/api';
import MetricCard from './charts/MetricCard';
import TrendChart from './charts/TrendChart';
import BarChart from './charts/BarChart';
import PieChart from './charts/PieChart';

export default function OverviewTab() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);

  useEffect(() => {
    loadData();
  }, [days]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const overview = await apiClient.getOverview(days);
      setData(overview);
    } catch (err) {
      setError('Failed to load overview data');
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

  const changeColor = data.change_percentage >= 0 ? 'text-red-600' : 'text-green-600';
  const changeIcon = data.change_percentage >= 0 ? '↑' : '↓';

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

      {/* Top-level metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          title="Total Reprints"
          value={data.total_reprints}
          subtitle={`vs ${data.previous_period_total} previous period`}
          change={data.change_percentage}
        />
        <MetricCard
          title="Top Products"
          value={data.top_products.length}
          subtitle={data.top_products[0]?.product_type || 'N/A'}
        />
        <MetricCard
          title="Top Facilities"
          value={data.top_facilities.length}
          subtitle={data.top_facilities[0]?.facility || 'N/A'}
        />
        <MetricCard
          title="Top Reasons"
          value={data.top_reasons.length}
          subtitle={data.top_reasons[0]?.reason || 'N/A'}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Reprint Trends</h3>
          <TrendChart data={data.trend} />
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Reprint Reasons</h3>
          <BarChart
            data={data.top_reasons.map((r) => ({
              name: r.reason,
              value: r.count,
            }))}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Product Distribution</h3>
          <PieChart
            data={data.top_products.map((p) => ({
              name: p.product_type,
              value: p.count,
            }))}
          />
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Facility Distribution</h3>
          <PieChart
            data={data.top_facilities.map((f) => ({
              name: f.facility,
              value: f.count,
            }))}
          />
        </div>
      </div>

      {/* Top lists */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Products</h3>
          <ul className="space-y-2">
            {data.top_products.slice(0, 5).map((product, idx) => (
              <li key={idx} className="flex justify-between">
                <span className="text-gray-700">{product.product_type}</span>
                <span className="font-semibold">{product.count}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Facilities</h3>
          <ul className="space-y-2">
            {data.top_facilities.slice(0, 5).map((facility, idx) => (
              <li key={idx} className="flex justify-between">
                <span className="text-gray-700">{facility.facility}</span>
                <span className="font-semibold">{facility.count}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Reasons</h3>
          <ul className="space-y-2">
            {data.top_reasons.slice(0, 5).map((reason, idx) => (
              <li key={idx} className="flex justify-between">
                <span className="text-gray-700">{reason.reason}</span>
                <span className="font-semibold">{reason.count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

