interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  change?: number;
}

export default function MetricCard({ title, value, subtitle, change }: MetricCardProps) {
  const changeColor = change !== undefined && change >= 0 ? 'text-red-600' : 'text-green-600';
  const changeIcon = change !== undefined && change >= 0 ? '↑' : '↓';

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <div className="mt-2">
        <div className="text-3xl font-bold text-gray-900">{value}</div>
        {subtitle && (
          <div className="text-sm text-gray-500 mt-1">{subtitle}</div>
        )}
        {change !== undefined && (
          <div className={`text-sm mt-1 ${changeColor}`}>
            {changeIcon} {Math.abs(change).toFixed(1)}%
          </div>
        )}
      </div>
    </div>
  );
}

