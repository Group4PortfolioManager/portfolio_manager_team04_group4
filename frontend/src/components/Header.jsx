import { portfolioSummary } from "../data/mockData";

function Header() {
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
          <strong className="positive">+${portfolioSummary.total_return.toLocaleString()}</strong>
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
