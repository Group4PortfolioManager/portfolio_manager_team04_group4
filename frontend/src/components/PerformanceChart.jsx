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
  const firstValue = performanceHistory[0].value;
  const lastValue = performanceHistory[performanceHistory.length - 1].value;
  const change = ((lastValue - firstValue) / firstValue) * 100;
  const performanceColor = change >= 0 ? "#22c55e" : "#ef444";
  const getPointChange = (value) => {
    return ((value - firstValue) / firstValue) * 100;
  }

  return (
    <div className="panel panel-performance">
      <div className="panel-header">
        <h2>Portfolio Performance</h2>
        <span className={`change-badge ${change >= 0 ? "positive" : "negative"}`}>
          {change >= 0 ? "+" : ""}{change.toFixed(1)}%
        </span>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={performanceHistory} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="performanceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#1fd67a" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#1fd67a" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#232a3a" />
          <XAxis dataKey="label"
            tickFormatter={(value, index) => {
              if (index === 0) return value;
              if (value !== performanceHistory[index - 1].label) {
                return value;
              }

              return "";
            }}
            tick={{ fontSize: 12, fill: "#8891a3" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={(value) => `$${Math.round(value / 1000)}k`}
            tick={{ fontSize: 12, fill: "#8891a3", fontFamily: "var(--mono)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value) => [
              `$${value.toLocaleString("en-US", {
                maximumFractionDigits: 2
              })}`,
              "Value"
            ]}
            contentStyle={{
              background: "#131824",
              border: "1px solid #232a3a",
              borderRadius: 8,
              color: "#e7e9ee"
            }}
            labelStyle={{ color: "#8891a3" }}
            labelFormatter={(label) => label}
            content={({ active, payload, label }) => {
              if (!active || !payload || !payload.length) return null;

              const value = payload[0].value;
              const percent = getPointChange(value);

              return (
                <div
                  style={{
                    background: "#131824",
                    border: "1px solid #232a3a",
                    borderRadius: 8,
                    padding: 10
                  }}
                >
                  <div style={{ color: "#8891a3" }}>
                    {label}
                  </div>

                  <div style={{ color: "#e7e9ee" }}>
                    ${value.toLocaleString("en-US", {
                      maximumFractionDigits: 2
                    })}
                  </div>

                  <div style={{
                    color: percent >= 0 ? "#22c55e" : "#ef4444"
                  }}>
                    {percent >= 0 ? "+" : ""}
                    {percent.toFixed(2)}%
                  </div>
                </div>
              );
            }}
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
