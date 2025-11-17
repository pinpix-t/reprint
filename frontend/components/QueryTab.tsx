import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../lib/api';
import TrendChart from './charts/TrendChart';
import BarChart from './charts/BarChart';
import { format, subDays } from 'date-fns';

export default function QueryTab() {
  const [startDate, setStartDate] = useState(format(subDays(new Date(), 30), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(new Date(), 'yyyy-MM-dd'));
  const [facility, setFacility] = useState('');
  const [productType, setProductType] = useState('');
  const [comparisonType, setComparisonType] = useState('week');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [metrics, setMetrics] = useState<any>(null);
  const [comparison, setComparison] = useState<any>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [facilities, setFacilities] = useState<any[]>([]);
  const [reasons, setReasons] = useState<any[]>([]);
  const [drilldownData, setDrilldownData] = useState<any>(null);
  const [drilldownType, setDrilldownType] = useState<'facility' | 'product' | null>(null);
  
  const isMountedRef = useRef(true);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    isMountedRef.current = true;
    loadData();
    
    // Cleanup: prevent state updates on unmounted component
    return () => {
      isMountedRef.current = false;
      // Cancel any pending requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [startDate, endDate, facility, productType]);

  const loadData = async () => {
    // Cancel previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    abortControllerRef.current = new AbortController();
    
    try {
      if (!isMountedRef.current) return;
      
      setLoading(true);
      setError(null);

      const [metricsData, comparisonData, trendData, productsData, facilitiesData, reasonsData] = await Promise.all([
        apiClient.getReprintMetrics(startDate, endDate),
        apiClient.getComparison(startDate, endDate, comparisonType),
        apiClient.getTrend(startDate, endDate, 'day'),
        apiClient.getProductMetrics(startDate, endDate),
        apiClient.getFacilityMetrics(startDate, endDate),
        apiClient.getReasonMetrics(startDate, endDate),
      ]);

      // Only update state if component is still mounted
      if (isMountedRef.current) {
        setMetrics(metricsData);
        setComparison(comparisonData);
        setTrend(trendData);
        setProducts(productsData);
        setFacilities(facilitiesData);
        setReasons(reasonsData);
      }
    } catch (err: any) {
      // Ignore abort errors
      if (err.name === 'AbortError') {
        return;
      }
      
      if (isMountedRef.current) {
        setError('Failed to load data');
        console.error(err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  };

  const handleDrilldown = async (type: 'facility' | 'product', value: string) => {
    try {
      if (!isMountedRef.current) return;
      
      setLoading(true);
      const days = Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24));
      
      let data;
      if (type === 'facility') {
        data = await apiClient.getFacilityDetails(value, days);
      } else {
        data = await apiClient.getProductDetails(value, days);
      }
      
      // Only update state if component is still mounted
      if (isMountedRef.current) {
        setDrilldownData(data);
        setDrilldownType(type);
      }
    } catch (err: any) {
      if (isMountedRef.current) {
        setError('Failed to load drilldown data');
        console.error(err);
      }
    } finally {
      if (isMountedRef.current) {
        setLoading(false);
      }
    }
  };

  if (loading && !metrics) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Facility</label>
            <select
              value={facility}
              onChange={(e) => setFacility(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">All Facilities</option>
              {facilities.map((f, idx) => (
                <option key={idx} value={f.facility}>{f.facility}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Product Type</label>
            <select
              value={productType}
              onChange={(e) => setProductType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">All Products</option>
              {products.map((p, idx) => (
                <option key={idx} value={p.product_type}>{p.product_type}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Comparison Period</label>
          <select
            value={comparisonType}
            onChange={(e) => setComparisonType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="year">Last Year</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Metrics */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Reprints</h3>
            <div className="text-3xl font-bold text-gray-900 mt-2">{metrics.total_reprints}</div>
          </div>
          {comparison && (
            <>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-medium text-gray-500">Previous Period</h3>
                <div className="text-3xl font-bold text-gray-900 mt-2">{comparison.previous}</div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-medium text-gray-500">Change</h3>
                <div className={`text-3xl font-bold mt-2 ${comparison.change_percentage >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {comparison.change_percentage >= 0 ? '+' : ''}{comparison.change_percentage.toFixed(1)}%
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {trend.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Trend</h3>
            <TrendChart data={trend} />
          </div>
        )}

        {reasons.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Top Reasons</h3>
            <BarChart
              data={reasons.slice(0, 10).map((r) => ({
                name: r.reason,
                value: r.count,
              }))}
            />
          </div>
        )}
      </div>

      {/* Data Tables */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Products</h3>
          <div className="space-y-2">
            {products.slice(0, 10).map((p, idx) => (
              <div
                key={idx}
                className="flex justify-between items-center p-2 hover:bg-gray-50 cursor-pointer"
                onClick={() => handleDrilldown('product', p.product_type)}
              >
                <span className="text-gray-700">{p.product_type}</span>
                <span className="font-semibold">{p.count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Facilities</h3>
          <div className="space-y-2">
            {facilities.slice(0, 10).map((f, idx) => (
              <div
                key={idx}
                className="flex justify-between items-center p-2 hover:bg-gray-50 cursor-pointer"
                onClick={() => handleDrilldown('facility', f.facility)}
              >
                <span className="text-gray-700">{f.facility}</span>
                <span className="font-semibold">{f.count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Top Reasons</h3>
          <div className="space-y-2">
            {reasons.slice(0, 10).map((r, idx) => (
              <div key={idx} className="flex justify-between items-center p-2">
                <span className="text-gray-700">{r.reason}</span>
                <span className="font-semibold">{r.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Drilldown */}
      {drilldownData && drilldownType && (
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">
              {drilldownType === 'facility' ? 'Facility' : 'Product'} Details: {drilldownData[drilldownType]}
            </h3>
            <button
              onClick={() => {
                setDrilldownData(null);
                setDrilldownType(null);
              }}
              className="text-gray-500 hover:text-gray-700"
            >
              Close
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Total Reprints: {drilldownData.total_reprints}</h4>
              {drilldownData.trend && drilldownData.trend.length > 0 && (
                <TrendChart data={drilldownData.trend} />
              )}
            </div>
            <div>
              <h4 className="font-semibold mb-2">
                {drilldownType === 'facility' ? 'Products' : 'Facilities'}
              </h4>
              <ul className="space-y-2">
                {Object.entries(drilldownData[drilldownType === 'facility' ? 'products' : 'facilities'])
                  .sort(([, a], [, b]) => (b as number) - (a as number))
                  .slice(0, 10)
                  .map(([key, value], idx) => (
                    <li key={idx} className="flex justify-between">
                      <span>{key}</span>
                      <span className="font-semibold">{value as number}</span>
                    </li>
                  ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

