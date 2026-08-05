import AssetsTable from "../components/AssetsTable";
import PortfolioSelector from "./PortfolioSelector";

function Settings() {
  return (
    <>
      <PortfolioSelector embedded />

      <div className="panel">
        <h2>Asset Types</h2>
        <AssetsTable />
      </div>
    </>
  );
}

export default Settings;
