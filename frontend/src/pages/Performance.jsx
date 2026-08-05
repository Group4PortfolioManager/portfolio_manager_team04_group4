import { useParams } from "react-router-dom";
import PerformanceChart from "../components/PerformanceChart";

function Performance() {
  const { portfolioId } = useParams();
  const activePortfolioId = Number.parseInt(portfolioId, 10);

  return (
    <PerformanceChart
      height={420}
      portfolioId={activePortfolioId}
    />
  );
}

export default Performance;
