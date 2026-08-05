import { useParams } from "react-router-dom";
import HoldingsTable from "../components/HoldingsTable";

function Holdings() {
  const { portfolioId } = useParams();
  const activePortfolioId = Number.parseInt(portfolioId, 10);

  return <HoldingsTable portfolioId={activePortfolioId} />;
}

export default Holdings;
