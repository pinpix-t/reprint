import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface BarData {
  name: string;
  value: number;
}

interface BarChartProps {
  data: BarData[];
  onItemClick?: (item: { name: string; value: number }) => void;
}

export default function BarChart({ data, onItemClick }: BarChartProps) {
  const handleClick = (chartData: any, index: number) => {
    if (onItemClick && chartData && index >= 0 && index < data.length) {
      const item = data[index];
      if (item && item.name !== undefined && item.value !== undefined) {
        onItemClick({ name: item.name, value: item.value });
      }
    }
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsBarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
        <YAxis />
        <Tooltip />
        <Bar 
          dataKey="value" 
          fill="#3b82f6" 
          onClick={onItemClick ? handleClick : undefined}
          style={onItemClick ? { cursor: 'pointer' } : undefined}
        />
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}

