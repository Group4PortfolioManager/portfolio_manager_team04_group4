import { Outlet, useParams, Navigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import HeaderWithModal from "./HeaderWithModal";

function AppLayout() {
  const { portfolioId } = useParams();
  const activePortfolioId = Number.parseInt(portfolioId, 10);

  if (!Number.isInteger(activePortfolioId) || activePortfolioId <= 0) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="app-shell">
      <Sidebar portfolioId={activePortfolioId} />

      <div className="app-content">
        <HeaderWithModal portfolioId={activePortfolioId} />

        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
