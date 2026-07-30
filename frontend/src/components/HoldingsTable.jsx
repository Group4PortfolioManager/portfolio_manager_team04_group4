import { useState, useEffect } from 'react';
import { Link } from "react-router-dom";
import { getHoldings } from '../services/api';
import HoldingRow from "./HoldingRow";

function HoldingsTable({ showLink = false }) {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchHoldings() {
      try {
        const { data } = await getHoldings(1); // portfolioId = 1
        setHoldings(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchHoldings();
  }, []);

  if (loading) return <div className="panel"><h2>Your Holdings</h2><p>Loading...</p></div>;
  if (error) return <div className="panel"><h2>Your Holdings</h2><p>Error: {error}</p></div>;

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
