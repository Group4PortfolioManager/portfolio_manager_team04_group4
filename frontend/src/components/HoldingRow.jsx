import { useState, useEffect } from 'react';
import { getHolding } from '../services/api';

function HoldingRow({ holdingId }) {
  const [holding, setHolding] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchHolding() {
      try {
        const { data } = await getHolding(holdingId);
        setHolding(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchHolding();
  }, [holdingId]);

  if (loading) return <tr><td colSpan="7">Loading...</td></tr>;
  if (error) return <tr><td colSpan="7">Error: {error}</td></tr>;
  if (!holding) return <tr><td colSpan="7">No data</td></tr>;

  return (
    <tr>
      <td className="ticker-symbol">{holding.ticker}</td>
      <td>{holding.company_name}</td>
      <td className="mono">{holding.shares}</td>
      <td className="mono">${holding.current_price}</td>
      <td className="mono">${holding.cost_basis}</td>
      <td className="mono">${holding.market_value}</td>

      <td className={holding.profit_loss >= 0 ? "positive" : "negative"}>
        {holding.profit_loss >= 0 ? "+" : ""}${holding.profit_loss}
      </td>

    </tr>
  );
}

export default HoldingRow;
