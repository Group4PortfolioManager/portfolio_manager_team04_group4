import { useState, useEffect } from "react";
import { getAssets } from "../services/api";
import { useDataRefresh } from "../services/refreshStore";

function AssetsTable() {
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
      <div className="panel panel-assets">
        <h2>Asset Catalog</h2>
        <p>Loading assets...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel panel-assets">
        <h2>Asset Catalog</h2>
        <p>Error loading assets: {error}</p>
      </div>
    );
  }

  if (assets.length === 0) {
    return (
      <div className="panel panel-assets">
        <h2>Asset Catalog</h2>
        <p>No assets for the moment</p>
      </div>
    );
  }

  return (
    <div className="panel panel-assets">
      <h2>Asset Catalog</h2>

      <table>
        <thead>
          <tr>
            <th>Asset ID</th>
            <th>Asset Type</th>
          </tr>
        </thead>

        <tbody>
          {assets.map((asset) => (
            <tr key={asset.asset_id}>
              <td className="mono">{asset.asset_id}</td>
              <td>{asset.asset_type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AssetsTable;
