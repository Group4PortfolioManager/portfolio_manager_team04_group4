import { Link } from "react-router-dom";
import { holdings } from "../data/mockData";
import HoldingRow from "./HoldingRow";

function HoldingsTable({ showLink = false }) {
  return (
    <div className="panel">
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
              key={holding.ticker}
              holding={holding}
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