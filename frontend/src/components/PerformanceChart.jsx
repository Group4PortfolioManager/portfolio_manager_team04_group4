import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";
import { performanceHistory } from "../data/mockData";

function PerformanceChart({ height = 220 }) {
  return (
    <div className="panel">
      <h2>Portfolio Performance</h2>

      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={performanceHistory} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="performanceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1fd67a" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#1fd67a" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#232a3a" />
          <XAxis dataKey="label" tick={{ fontSize: 12, fill: "#8891a3" }} axisLine={false} tickLine={false} />
          <YAxis
            tickFormatter={(value) => `$${Math.round(value / 1000)}k`}
            tick={{ fontSize: 12, fill: "#8891a3", fontFamily: "var(--mono)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value) => [`$${value.toLocaleString()}`, "Value"]}
            contentStyle={{ background: "#131824", border: "1px solid #232a3a", borderRadius: 8, color: "#e7e9ee" }}
            labelStyle={{ color: "#8891a3" }}
          />

          <Area
            type="monotone"
            dataKey="value"
            stroke="#1fd67a"
            strokeWidth={2}
            fill="url(#performanceFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PerformanceChart;
