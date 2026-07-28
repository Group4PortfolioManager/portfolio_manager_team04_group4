import AssetAllocation from "../components/AssetAllocation";
import PerformanceChart from "../components/PerformanceChart";
import HoldingsTable from "../components/HoldingsTable";
import StatTile from "../components/StatTile";
import { assetAllocation } from "../data/mockData";

function Dashboard() {
  return (
    <div className="dashboard-grid">
      <AssetAllocation />
      <PerformanceChart />

      <div className="span-2">
        <HoldingsTable showLink />
      </div>

      <div className="stat-tile-row span-2">
        {assetAllocation.map((asset) => (
          <StatTile
            key={asset.type}
            label={asset.type === "Cash" ? "Cash Balance" : `${asset.type} Value`}
            value={`$${asset.value.toLocaleString()}`}
          />
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
