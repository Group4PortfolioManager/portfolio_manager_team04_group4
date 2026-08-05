function Header({
  portfolioId,
  portfolioName,
  onAddAsset,
  onRemoveAsset,
  onDepositCash,
  onWithdrawCash,
  summary,
}) {
  const totalValue = summary?.total_value ?? 0;
  const totalReturn = summary?.total_return ?? 0;
  const costBasis = summary?.cost_basis_total ?? 0;
  const totalReturnPercent = costBasis ? (totalReturn / costBasis) * 100 : 0;
  const daysGain = summary?.day_gain ?? 0;
  const daysGainPercent = summary?.day_gain_percent ?? 0;

  return (
    <header className="topbar">
      <div className="topbar-left">
        <h1>Portfolio Manager</h1>
        <span className="live-dot">
          {portfolioName || `Portfolio #${portfolioId}`} | Live market data
        </span>
      </div>

      <div className="topbar-stats">
        <span className="stat-pill">
          Total Portfolio Value
          <strong>${totalValue.toLocaleString()}</strong>
        </span>

        <span className="stat-pill">
          Total Return
          <strong className="positive">
            +${totalReturn.toLocaleString()}
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
        <button type="button" className="btn btn-secondary" onClick={onDepositCash}>Deposit Cash</button>
        <button type="button" className="btn btn-secondary" onClick={onWithdrawCash}>Withdraw Cash</button>
        <button type="button" className="btn btn-primary" onClick={onAddAsset}>+ Add Asset</button>
        <button type="button" className="btn btn-secondary" onClick={onRemoveAsset}>Remove Asset</button>
      </div>
    </header>
  );
}

export default Header;
