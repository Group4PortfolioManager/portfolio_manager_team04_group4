import { portfolioSummary, performanceHistory } from "../data/mockData";

function Header() {
  const previousValue = performanceHistory[performanceHistory.length - 2].value;
  const daysGain = performanceHistory[performanceHistory.length - 1].value - previousValue;
  const daysGainPercent = (daysGain / previousValue) * 100;

  const costBasis = portfolioSummary.total_value - portfolioSummary.total_return;
  const totalReturnPercent = (portfolioSummary.total_return / costBasis) * 100;

  return (
    <header className="topbar">
      <div>
        <h1>Portfolio Manager</h1>
        <span className="live-dot">Live market data</span>
      </div>

      <div className="topbar-stats">
        <span className="stat-pill">
          Total Portfolio Value
          <strong>${portfolioSummary.total_value.toLocaleString()}</strong>
        </span>

        <span className="stat-pill">
          Total Return
          <strong className="positive">
            +${portfolioSummary.total_return.toLocaleString()}
            <span className="stat-pct positive"> (+{totalReturnPercent.toFixed(1)}%)</span>
          </strong>
        </span>

        <span className="stat-pill">
          Day's Gain
          <strong className={daysGain >= 0 ? "positive" : "negative"}>
            {daysGain >= 0 ? "+" : "-"}${Math.abs(daysGain).toLocaleString()}
            <span className={`stat-pct ${daysGain >= 0 ? "positive" : "negative"}`}>
              {" "}({daysGain >= 0 ? "+" : "-"}{Math.abs(daysGainPercent).toFixed(1)}%)
            </span>
          </strong>
        </span>
      </div>

      <div className="topbar-actions">
        <button type="button" className="btn btn-primary">+ Add Asset</button>
        <button type="button" className="btn btn-secondary">Remove Asset</button>
      </div>
    </header>
  );
}

export default Header;
