import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../lib/api';
import { useFilters } from '../contexts/FilterContext';
import GlobalFilters from './GlobalFilters';
import HeatmapChart from './charts/HeatmapChart';
import TrendChart from './charts/TrendChart';
import BarChart from './charts/BarChart';
import PieChart from './charts/PieChart';
import { exportToCSV } from '../utils/export';

export default function QueryTab() {
  const { filters, setFilters } = useFilters();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [matrix, setMatrix] = useState<any[]>([]);
  const [trend, setTrend] = useState<any[]>([]);
  const [reasons, setReasons] = useState<any[]>([]);
  const [records, setRecords] = useState<any[]>([]);
  const [recordsTotal, setRecordsTotal] = useState(0);
  const [recordsPage, setRecordsPage] = useState(0);
  const recordsPerPage = 50;
  
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    loadData();
    
    return () => {
      isMountedRef.current = false;
    };
  }, [filters, recordsPage]);

  const loadData = async () => {
    try {
      if (!isMountedRef.current) return;
      
      setLoading(true);
      setError(null);

      const startDate = filters.startDate || undefined;
      const endDate = filters.endDate || undefined;

      // Load matrix for heatmap
      const matrixDataFull = await apiClient.getMatrix(startDate, endDate);

      // Load trend if filtered
      let trendData: any[] = [];
      if (filters.facility || filters.productType) {
        trendData = await apiClient.getTrend(
          startDate || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
          endDate || new Date().toISOString().split('T')[0]
        );
      }

      // Load reasons breakdown
      let reasonsData: any[] = [];
      if (filters.facility || filters.productType) {
        const drilldownType = filters.facility ? 'facility' : 'product';
        const drilldownValue = filters.facility || filters.productType || '';
        const days = startDate && endDate 
          ? Math.ceil((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24))
          : 30;
        
        const drilldown = drilldownType === 'facility'
          ? await apiClient.getFacilityDetails(drilldownValue, days)
          : await apiClient.getProductDetails(drilldownValue, days);
        
        reasonsData = Object.entries(drilldown.reasons || {}).map(([reason, count]) => ({
          reason,
          count: count as number,
        }));
      } else {
        reasonsData = await apiClient.getReasonMetrics(startDate, endDate, 10);
      }

      // Load records
      const recordsData = await apiClient.getReprintRecords(
        startDate,
        endDate,
        filters.facility || undefined,
        filters.productType || undefined,
        filters.reasonCategory || undefined,
        filters.shippingCountry || undefined,
        filters.shippingService || undefined,
        recordsPerPage,
        recordsPage * recordsPerPage
      );

      if (isMountedRef.current) {
        setMatrix(matrixDataFull);
        setTrend(trendData);
        setReasons(reasonsData);
        setRecords(recordsData.records || []);
        setRecordsTotal(recordsData.total || 0);
      }
    } catch (err: any) {
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

  const handleHeatmapClick = (facility: string, product: string) => {
    setFilters({ facility, productType: product });
  };

  const handleExport = () => {
    exportToCSV(records, 'reprints.csv');
  };

  if (loading && matrix.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading...</div>
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
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Product × Facility Heatmap */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Product × Facility Heatmap</h3>
          <p className="text-sm text-gray-500 mb-4">Click any cell to filter by that Product-Facility combination</p>
          {matrix.length > 0 ? (
            <HeatmapChart
              data={matrix.map((m) => ({
                facility: m.facility,
                product: m.product,
                count: m.count,
              }))}
              onCellClick={handleHeatmapClick}
            />
          ) : (
            <div className="text-center text-gray-500 py-8">No data available</div>
          )}
        </div>

        {/* Time-series for selected product/facility */}
        {(filters.facility || filters.productType) && trend.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">
              Trend for {filters.facility || filters.productType}
            </h3>
            <TrendChart data={trend} />
          </div>
        )}

        {/* Reason breakdown for selected product/facility */}
        {(filters.facility || filters.productType) && reasons.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Reason Breakdown</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BarChart
                data={reasons.map((r) => ({
                  name: r.reason,
                  value: r.count,
                }))}
              />
              <PieChart
                data={reasons.map((r) => ({
                  name: r.reason,
                  value: r.count,
                }))}
              />
            </div>
          </div>
        )}

        {/* Detailed Records Table */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">Detailed Records</h3>
            <button
              onClick={handleExport}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              Export to CSV
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sub Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Facility</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Country</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Service</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">MO#</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CO#</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {records.map((record, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                      {record.requested_date ? new Date(record.requested_date).toLocaleDateString() : '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.order_number || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.product_type || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.sub_type || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.facility || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.reprint_reason || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.shipping_country || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.shipping_service || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.monumber || '-'}</td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{record.conumber || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {recordsTotal > recordsPerPage && (
            <div className="mt-4 flex justify-between items-center">
              <div className="text-sm text-gray-500">
                Showing {recordsPage * recordsPerPage + 1} to {Math.min((recordsPage + 1) * recordsPerPage, recordsTotal)} of {recordsTotal} records
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setRecordsPage(Math.max(0, recordsPage - 1))}
                  disabled={recordsPage === 0}
                  className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setRecordsPage(recordsPage + 1)}
                  disabled={(recordsPage + 1) * recordsPerPage >= recordsTotal}
                  className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
