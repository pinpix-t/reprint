import { useState, useEffect, useRef, useCallback } from 'react';
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

  const loadData = useCallback(async () => {
    try {
      if (!isMountedRef.current) return;
      
      setLoading(true);
      setError(null);

      const startDate = filters.startDate || undefined;
      const endDate = filters.endDate || undefined;

      // Load matrix for heatmap
      let matrixDataFull = await apiClient.getMatrix(startDate, endDate);
      
      // Filter matrix by facility/productType if filters are set
      if (filters.facility || filters.productType) {
        matrixDataFull = matrixDataFull.filter((m: any) => {
          if (filters.facility && m.facility !== filters.facility) return false;
          if (filters.productType && m.product !== filters.productType) return false;
          return true;
        });
      }

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
        filters.reprintReason || undefined,
        filters.shippingCountry || undefined,
        filters.region || undefined,
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
  }, [filters, recordsPage, recordsPerPage]);

  useEffect(() => {
    isMountedRef.current = true;
    // Reset to first page when filters change
    setRecordsPage(0);
    
    return () => {
      isMountedRef.current = false;
    };
  }, [filters]);

  // Load data when filters or pagination changes
  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleHeatmapClick = (facility: string, product: string) => {
    setFilters({ facility, productType: product, reprintReason: null });
  };

  const handleReasonClick = (item: { name: string; value: number }) => {
    setFilters({ reprintReason: item.name });
  };

  const handleBreadcrumbClick = (level: 'all' | 'product-facility' | 'reason' | 'orders') => {
    if (level === 'all') {
      setFilters({ facility: null, productType: null, reprintReason: null });
    } else if (level === 'product-facility') {
      setFilters({ reprintReason: null });
    } else if (level === 'reason') {
      // Go back to reason view (clear reprintReason but keep facility/productType)
      setFilters({ reprintReason: null });
    }
    // 'orders' level is disabled - no action needed
  };

  const handleExport = () => {
    exportToCSV(records, 'reprints.csv');
  };

  // Build breadcrumb path
  const getBreadcrumbs = () => {
    const crumbs: Array<{ label: string; level: 'all' | 'product-facility' | 'reason' | 'orders'; active: boolean }> = [];
    
    if (!filters.facility && !filters.productType && !filters.reprintReason) {
      crumbs.push({ label: 'All', level: 'all', active: true });
    } else {
      crumbs.push({ label: 'All', level: 'all', active: false });
      
      if (filters.facility || filters.productType) {
        const label = filters.facility && filters.productType 
          ? `${filters.productType} × ${filters.facility}`
          : filters.facility || filters.productType || '';
        crumbs.push({ label, level: 'product-facility', active: !filters.reprintReason });
        
        if (filters.reprintReason) {
          crumbs.push({ label: filters.reprintReason, level: 'reason', active: true });
          crumbs.push({ label: 'Orders', level: 'orders', active: true });
        }
      }
    }
    
    return crumbs;
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

        {/* Breadcrumb Navigation */}
        {(filters.facility || filters.productType || filters.reprintReason) && (
          <div className="bg-white p-4 rounded-lg shadow">
            <nav className="flex items-center space-x-2 text-sm">
              {getBreadcrumbs().map((crumb, index) => (
                <div key={index} className="flex items-center">
                  {index > 0 && <span className="mx-2 text-gray-400">/</span>}
                  <button
                    onClick={() => handleBreadcrumbClick(crumb.level)}
                    className={`${
                      crumb.active
                        ? 'text-blue-600 font-semibold'
                        : 'text-gray-600 hover:text-blue-600'
                    } transition-colors`}
                    disabled={crumb.level === 'orders'}
                  >
                    {crumb.label}
                  </button>
                </div>
              ))}
            </nav>
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
        {(filters.facility || filters.productType) && !filters.reprintReason && reasons.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">Reason Breakdown</h3>
            <p className="text-sm text-gray-500 mb-4">Click on a reason to see the orders</p>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <BarChart
                data={reasons.map((r) => ({
                  name: r.reason,
                  value: r.count,
                }))}
                onItemClick={handleReasonClick}
              />
              <PieChart
                data={reasons.map((r) => ({
                  name: r.reason,
                  value: r.count,
                }))}
                onItemClick={handleReasonClick}
              />
            </div>
          </div>
        )}

        {/* Detailed Records Table */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">
              {filters.reprintReason 
                ? `Orders for: ${filters.reprintReason}`
                : filters.facility || filters.productType
                ? `Orders for: ${filters.facility || filters.productType}`
                : 'Detailed Records'}
            </h3>
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
