import { useFilters } from '../../contexts/FilterContext';

interface HeatmapData {
  facility: string;
  product: string;
  count: number;
}

interface HeatmapChartProps {
  data: HeatmapData[];
  onCellClick?: (facility: string, product: string) => void;
}

export default function HeatmapChart({ data, onCellClick }: HeatmapChartProps) {
  const { setFilters } = useFilters();

  // Get unique facilities and products
  const facilities = Array.from(new Set(data.map((d) => d.facility))).sort();
  const products = Array.from(new Set(data.map((d) => d.product))).sort();

  // Create a map for quick lookup
  const dataMap = new Map<string, number>();
  data.forEach((d) => {
    dataMap.set(`${d.facility}-${d.product}`, d.count);
  });

  // Find max count for color scaling
  const maxCount = Math.max(...data.map((d) => d.count), 1);

  const getColor = (count: number) => {
    const intensity = count / maxCount;
    if (intensity === 0) return 'bg-gray-100';
    if (intensity < 0.2) return 'bg-blue-100';
    if (intensity < 0.4) return 'bg-blue-300';
    if (intensity < 0.6) return 'bg-blue-500';
    if (intensity < 0.8) return 'bg-blue-700';
    return 'bg-blue-900';
  };

  const handleCellClick = (facility: string, product: string) => {
    if (onCellClick) {
      onCellClick(facility, product);
    } else {
      // Default behavior: update filters
      setFilters({ facility, productType: product });
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse">
        <thead>
          <tr>
            <th className="border border-gray-300 p-2 bg-gray-50 text-xs font-medium text-gray-700 sticky left-0 z-10">
              Facility / Product
            </th>
            {products.map((product) => (
              <th
                key={product}
                className="border border-gray-300 p-2 bg-gray-50 text-xs font-medium text-gray-700 min-w-[100px]"
              >
                <div className="transform -rotate-45 origin-center whitespace-nowrap">{product}</div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {facilities.map((facility) => (
            <tr key={facility}>
              <td className="border border-gray-300 p-2 bg-gray-50 text-xs font-medium text-gray-700 sticky left-0 z-10">
                {facility}
              </td>
              {products.map((product) => {
                const count = dataMap.get(`${facility}-${product}`) || 0;
                return (
                  <td
                    key={`${facility}-${product}`}
                    className={`border border-gray-300 p-2 text-center text-xs cursor-pointer hover:opacity-80 ${getColor(
                      count
                    )}`}
                    onClick={() => handleCellClick(facility, product)}
                    title={`${facility} × ${product}: ${count} reprints`}
                  >
                    {count > 0 ? count : ''}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

