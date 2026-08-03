import { useState, useEffect } from "react";
import { getAssets } from "../services/api";
import { useDataRefresh } from "../services/refreshStore";
import { PieChart, Pie, Cell, Tooltip } from "recharts";

const COLORS = {
  'Stock': '#3b82f6',
  'Bond': '#22d3ee',
  'Crypto': '#f59e0b',
  'Cash': '#a78bfa'
};

function AssetAllocation() {
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const refreshKey = useDataRefresh();

  useEffect(() => {
    getAssets()
      .then((result) => {
        const assetsData = Array.isArray(result.data) ? result.data : [];
        setAssets(assetsData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [refreshKey]);

  if (loading) {
    return (
      <div className="panel">
        <h2>Asset Allocation</h2>
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel">
        <h2>Asset Allocation</h2>
        <p>Error loading assets: {error}</p>
      </div>
    );
  }

  if (assets.length === 0) {
    return (
      <div className="panel">
        <h2>Asset Allocation</h2>
        <p>No assets for the moment</p>
      </div>
    );
  }

  const total = assets.length;
  const allocation = assets.reduce((acc, asset) => {
    const type = asset.asset_type || 'Stock';
    const label = type === 'Stock' ? 'Stocks' : type === 'Bond' ? 'Bonds' : type === 'Crypto' ? 'Crypto' : 'Cash';
    acc[label] = (acc[label] || 0) + 1;
    return acc;
  }, {});

  const data = Object.entries(allocation).map(([type, count]) => ({
    type,
    percentage: Math.round((count / total) * 100),
    color: COLORS[type] || '#8891a3'
  }));

  return (
    <div className="panel">
      <h2>Asset Allocation</h2>

      <div className="donut-row">
        <PieChart width={220} height={220}>
          <Pie
            data={data}
            dataKey="percentage"
            nameKey="type"
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
          >
            {data.map((entry) => (
              <Cell key={entry.type} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => [`${value}%`, "Allocation"]}
            contentStyle={{ background: "#131824", border: "1px solid #232a3a", borderRadius: 8, color: "#e7e9ee" }}
            labelStyle={{ color: "#8891a3" }}
          />
        </PieChart>

        <ul className="legend">
          {data.map((asset) => (
            <li key={asset.type}>
              <span className="legend-dot" style={{ backgroundColor: asset.color }} />
              {asset.type}
              <span className="legend-percentage">{asset.percentage}%</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default AssetAllocation;
