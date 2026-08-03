import { useEffect, useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";
import { getPortfolioPerformance } from "../services/api";
import { useDataRefresh } from "../services/refreshStore";

const WINDOW_SIZES = {
  months: 12,
  days: 7,
};

function PerformanceChart({ height = 220, portfolioId = 1 }) {
  const [performanceHistory, setPerformanceHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [windowType, setWindowType] = useState("months");
  const refreshKey = useDataRefresh();

  useEffect(() => {
    let isMounted = true;

    async function loadPerformance() {
      setLoading(true);
      setError(null);

      try {
        const result = await getPortfolioPerformance(
          portfolioId,
          windowType,
          WINDOW_SIZES[windowType]
        );
        if (!isMounted) return;

        if (result.response.ok) {
          setPerformanceHistory(result.data?.history || []);
        } else {
          setError(result.data?.error || "Failed to load performance history.");
          setPerformanceHistory([]);
        }
      } catch (err) {
        if (!isMounted) return;
        setError(err.message || "Failed to load performance history.");
        setPerformanceHistory([]);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadPerformance();

    return () => {
      isMounted = false;
    };
  }, [portfolioId, windowType, refreshKey]);

  const firstValue = performanceHistory[0]?.value ?? 0;
  const lastValue = performanceHistory[performanceHistory.length - 1]?.value ?? 0;
  const change = useMemo(() => {
    if (!firstValue) return 0;
    return ((lastValue - firstValue) / firstValue) * 100;
  }, [firstValue, lastValue]);

  const getPointChange = (value) => {
    if (!firstValue) return 0;
    return ((value - firstValue) / firstValue) * 100;
  };

  if (loading) {
    return (
      <div className="panel panel-performance">
        <div className="panel-header">
          <h2>Portfolio Performance</h2>
        </div>
        <div style={{ color: "#8891a3", padding: 16 }}>Loading performance...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel panel-performance">
        <div className="panel-header">
          <h2>Portfolio Performance</h2>
        </div>
        <div style={{ color: "#ef4444", padding: 16 }}>{error}</div>
      </div>
    );
  }

  if (!performanceHistory.length) {
    return (
      <div className="panel panel-performance">
        <div className="panel-header">
          <h2>Portfolio Performance</h2>
        </div>
        <div style={{ color: "#8891a3", padding: 16 }}>No performance history available.</div>
      </div>
    );
  }

  return (
    <div className="panel panel-performance">
      <div className="panel-header">
        <div className="panel-title-row">
          <h2>Portfolio Performance</h2>
          <div className="window-toggle" role="group" aria-label="Performance window">
            <button
              type="button"
              className={`window-toggle-btn ${windowType === "months" ? "active" : ""}`}
              onClick={() => setWindowType("months")}
            >
              Yearly
            </button>
            <button
              type="button"
              className={`window-toggle-btn ${windowType === "days" ? "active" : ""}`}
              onClick={() => setWindowType("days")}
            >
              Weekly
            </button>
          </div>
        </div>
        <span className={`change-badge ${change >= 0 ? "positive" : "negative"}`}>
          {change >= 0 ? "+" : ""}
          {change.toFixed(1)}%
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
              if (windowType === "days") {
                return value;
              }

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
