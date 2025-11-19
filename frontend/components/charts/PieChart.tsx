import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

interface PieData {
  name: string;
  value: number;
}

interface PieChartProps {
  data: PieData[];
  onItemClick?: (item: { name: string; value: number }) => void;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'];

export default function PieChart({ data, onItemClick }: PieChartProps) {
  const handleClick = (clickedData: any, index: number) => {
    if (onItemClick && clickedData && index >= 0 && index < data.length) {
      const item = data[index];
      if (item && item.name !== undefined && item.value !== undefined) {
        onItemClick({ name: item.name, value: item.value });
      }
    }
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          outerRadius={80}
          fill="#8884d8"
          dataKey="value"
          onClick={onItemClick ? handleClick : undefined}
          style={onItemClick ? { cursor: 'pointer' } : undefined}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </RechartsPieChart>
    </ResponsiveContainer>
  );
}

