import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getHoldings } from "../services/api";
import HoldingRow from "./HoldingRow";

function HoldingsTable({ showLink = false }) {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getHoldings(1)
      .then((result) => {
        const holdingsData = Array.isArray(result.data) ? result.data : [];
        setHoldings(holdingsData);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="panel panel-holdings">
        <h2>Your Holdings</h2>
        <p>Loading holdings...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="panel panel-holdings">
        <h2>Your Holdings</h2>
        <p>Error loading holdings: {error}</p>
      </div>
    );
  }

  if (holdings.length === 0) {
    return (
      <div className="panel panel-holdings">
        <h2>Your Holdings</h2>
        <p>No holdings for the moment</p>
      </div>
    );
  }

  return (
    <div className="panel panel-holdings">
      <h2>Your Holdings</h2>

      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Company Name</th>
            <th>Shares</th>
            <th>Current Price</th>
            <th>Cost Basis</th>
            <th>Market Value</th>
            <th>P/L</th>
          </tr>
        </thead>

        <tbody>
          {holdings.map((holding) => (
            <HoldingRow
              key={holding.holding_id}
              holdingId={holding.holding_id}
            />
          ))}
        </tbody>
      </table>

      {showLink && (
        <Link to="/holdings" className="text-link">Add or Remove Holdings</Link>
      )}
    </div>
  );
}

export default HoldingsTable;