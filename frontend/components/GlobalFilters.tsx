import { useState, useEffect } from 'react';
import { useFilters } from '../contexts/FilterContext';
import { apiClient } from '../lib/api';
import { format, subDays } from 'date-fns';

export default function GlobalFilters() {
  const { filters, setFilters } = useFilters();
  const [products, setProducts] = useState<string[]>([]);
  const [facilities, setFacilities] = useState<string[]>([]);
  const [shippingCountries, setShippingCountries] = useState<string[]>([]);
  const [shippingServices, setShippingServices] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFilterOptions = async () => {
    setLoading(true);
    try {
      const [productsData, facilitiesData, countriesData, servicesData] = await Promise.all([
        apiClient.getProductMetrics(undefined, undefined, 100),
        apiClient.getFacilityMetrics(undefined, undefined, 100),
        apiClient.getShippingCountryMetrics(undefined, undefined, 100),
        apiClient.getShippingServiceMetrics(undefined, undefined, 100),
      ]);

      setProducts(productsData.map((p: any) => p.product_type));
      setFacilities(facilitiesData.map((f: any) => f.facility));
      setShippingCountries(countriesData.map((c: any) => c.country));
      setShippingServices(servicesData.map((s: any) => s.service));
    } catch (error) {
      console.error('Failed to load filter options:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDateChange = (field: 'startDate' | 'endDate', value: string) => {
    setFilters({ [field]: value || null });
  };

  const handleSelectChange = (field: keyof typeof filters, value: string) => {
    setFilters({ [field]: value || null });
  };

  const reasonCategories = [
    'All',
    'Damage/Print Quality',
    'Packaging/Transit Damage',
    'Address/Undelivered',
    'Customer Error',
  ];

  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <h3 className="text-lg font-semibold mb-4">Filters</h3>
      <div className="space-y-4">
        {/* Date Range */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              type="date"
              value={filters.startDate || ''}
              onChange={(e) => handleDateChange('startDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              type="date"
              value={filters.endDate || ''}
              onChange={(e) => handleDateChange('endDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
            />
          </div>
        </div>

        {/* Product Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Product Type</label>
          <select
            value={filters.productType || ''}
            onChange={(e) => handleSelectChange('productType', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Products</option>
            {products.map((product) => (
              <option key={product} value={product}>
                {product}
              </option>
            ))}
          </select>
        </div>

        {/* Facility */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Facility</label>
          <select
            value={filters.facility || ''}
            onChange={(e) => handleSelectChange('facility', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Facilities</option>
            {facilities.map((facility) => (
              <option key={facility} value={facility}>
                {facility}
              </option>
            ))}
          </select>
        </div>

        {/* Reason Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Reason Category</label>
          <select
            value={filters.reasonCategory || ''}
            onChange={(e) => handleSelectChange('reasonCategory', e.target.value === 'All' ? null : e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            {reasonCategories.map((category) => (
              <option key={category} value={category === 'All' ? '' : category}>
                {category}
              </option>
            ))}
          </select>
        </div>

        {/* Shipping Country */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Shipping Country</label>
          <select
            value={filters.shippingCountry || ''}
            onChange={(e) => handleSelectChange('shippingCountry', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Countries</option>
            {shippingCountries.map((country) => (
              <option key={country} value={country}>
                {country}
              </option>
            ))}
          </select>
        </div>

        {/* Shipping Service */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Shipping Service</label>
          <select
            value={filters.shippingService || ''}
            onChange={(e) => handleSelectChange('shippingService', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="">All Services</option>
            {shippingServices.map((service) => (
              <option key={service} value={service}>
                {service}
              </option>
            ))}
          </select>
        </div>

        {/* Reset Button */}
        <button
          onClick={() => setFilters({
            startDate: null,
            endDate: null,
            productType: null,
            subType: null,
            facility: null,
            reasonCategory: null,
            shippingCountry: null,
            shippingService: null,
          })}
          className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 text-sm font-medium"
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
}

