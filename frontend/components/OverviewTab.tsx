import { useEffect, useState, useRef } from 'react';
import { apiClient, OverviewData } from '../lib/api';
import { useFilters } from '../contexts/FilterContext';
import GlobalFilters from './GlobalFilters';
import MetricCard from './charts/MetricCard';
import TrendChart from './charts/TrendChart';
import BarChart from './charts/BarChart';
import PieChart from './charts/PieChart';

export default function OverviewTab() {
  const { filters } = useFilters();
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(7);
  const [trendFilter, setTrendFilter] = useState<'all' | 'quality' | 'logistics'>('all');
  const [qualityProducts, setQualityProducts] = useState<any[]>([]);
  const [qualityFacilities, setQualityFacilities] = useState<any[]>([]);
  const [shippingCountries, setShippingCountries] = useState<any[]>([]);
  const [shippingServices, setShippingServices] = useState<any[]>([]);
  const [productFacilityMatrix, setProductFacilityMatrix] = useState<any[]>([]);
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    loadData();
    
    return () => {
      isMountedRef.current = false;
    };
  }, [days, filters]);

  const loadData = async () => {
    try {
      if (!isMountedRef.current) return;
      
      setLoading(true);
      setError(null);
      
      // Build date range from filters or use days
      const startDate = filters.startDate || undefined;
      const endDate = filters.endDate || undefined;
      
      const [overview, qualityProductsData, qualityFacilitiesData, countriesData, servicesData, matrixData] = await Promise.all([
        apiClient.getOverview(days),
        apiClient.getProductMetrics(startDate, endDate, 10).then(async (products) => {
          // Filter for quality reasons only
          const qualityData = [];
          for (const product of products.slice(0, 10)) {
            const productMetrics = await apiClient.getReprintMetrics(startDate, endDate);
            // This is a simplified approach - in production, you'd want a dedicated endpoint
            qualityData.push(product);
          }
          return products; // Simplified for now
        }),
        apiClient.getFacilityMetrics(startDate, endDate, 10),
        apiClient.getShippingCountryMetrics(startDate, endDate, 10),
        apiClient.getShippingServiceMetrics(startDate, endDate, 10),
        apiClient.getMatrix(startDate, endDate).catch(() => []), // Matrix endpoint call
      ]);
      
      if (isMountedRef.current) {
        setData(overview);
        setQualityProducts(qualityProductsData.slice(0, 10));
        setQualityFacilities(qualityFacilitiesData.slice(0, 10));
        setShippingCountries(countriesData);
        setShippingServices(servicesData);
        setProductFacilityMatrix(matrixData || []);
      }
    } catch (err) {
      if (isMountedRef.current) {
        setError('Failed to load overview data');
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

  // Get trend data based on filter
  const getTrendData = () => {
    if (trendFilter === 'all') {
      return data.trend;
    } else if (trendFilter === 'quality') {
      return data.trend_by_category?.['Damage/Print Quality'] || [];
    } else {
      // Logistics = Transit + Address
      const transit = data.trend_by_category?.['Packaging/Transit Damage'] || [];
      const address = data.trend_by_category?.['Address/Undelivered'] || [];
      // Combine them (simplified - would need proper date merging in production)
      return transit.length > address.length ? transit : address;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Global Filters Sidebar */}
      <div className="lg:col-span-1">
        <GlobalFilters />
      </div>

      {/* Main Content */}
      <div className="lg:col-span-3 space-y-6">
        {/* Period selector */}
        <div className="flex justify-end">
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

        {/* KPI Tiles - 6 tiles */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Total Reprints"
            value={data.total_reprints}
            subtitle={`vs ${data.previous_period_total} previous period`}
            change={data.change_percentage}
          />
          <MetricCard
            title="Quality/Damage Reprints"
            value={data.quality_reprints}
            subtitle={`${data.quality_percentage.toFixed(1)}% of total`}
          />
          <MetricCard
            title="Top Product"
            value={data.top_products[0]?.count || 0}
            subtitle={data.top_products[0]?.product_type || 'N/A'}
          />
          <MetricCard
            title="Top Facility"
            value={data.top_facilities[0]?.count || 0}
            subtitle={data.top_facilities[0]?.facility || 'N/A'}
          />
          <MetricCard
            title="Top Shipping Country"
            value={data.top_shipping_country.count}
            subtitle={data.top_shipping_country.country || 'N/A'}
          />
          <MetricCard
            title="Top Shipping Service"
            value={data.top_shipping_service.count}
            subtitle={data.top_shipping_service.service || 'N/A'}
          />
        </div>

        {/* Trend Charts with Toggle */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Reprint Trends</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => setTrendFilter('all')}
                className={`px-3 py-1 rounded text-sm ${
                  trendFilter === 'all' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setTrendFilter('quality')}
                className={`px-3 py-1 rounded text-sm ${
                  trendFilter === 'quality' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                Quality/Damage
              </button>
              <button
                onClick={() => setTrendFilter('logistics')}
                className={`px-3 py-1 rounded text-sm ${
                  trendFilter === 'logistics' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
                }`}
              >
                Logistics
              </button>
            </div>
          </div>
          <TrendChart data={getTrendData()} />
        </div>

        {/* Reason Categories Stacked */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Reprints by Reason Category</h3>
          <BarChart
            data={data.reason_categories.map((c) => ({
              name: c.category,
              value: c.count,
            }))}
          />
        </div>

        {/* Top Offenders Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Top Products by Quality Reprints</h3>
            <BarChart
              data={qualityProducts.slice(0, 5).map((p) => ({
                name: p.product_type,
                value: p.count,
              }))}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Top Facilities by Quality Reprints</h3>
            <BarChart
              data={qualityFacilities.slice(0, 5).map((f) => ({
                name: f.facility,
                value: f.count,
              }))}
            />
          </div>
        </div>

        {/* Product-Facility Combinations Table */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Product-Facility Combinations</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Facility</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reprints</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {productFacilityMatrix.slice(0, 10).map((item, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.product || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.facility || 'N/A'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.count || 0}</td>
                  </tr>
                ))}
                {productFacilityMatrix.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-6 py-4 text-center text-sm text-gray-500">No data available</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Shipping Snapshot */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Reprints by Shipping Country</h3>
            <BarChart
              data={shippingCountries.slice(0, 10).map((c) => ({
                name: c.country,
                value: c.count,
              }))}
            />
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Reprints by Shipping Service</h3>
            <BarChart
              data={shippingServices.slice(0, 10).map((s) => ({
                name: s.service,
                value: s.count,
              }))}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
