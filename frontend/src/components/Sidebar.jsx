import {
  useEffect,
  useState,
} from "react";
import {
  NavLink,
  useNavigate,
} from "react-router-dom";
import { LayoutDashboard, FileText, TrendingUp, Settings, ChartCandlestick } from "lucide-react";
import { getPortfolios } from "../services/api";
import { useDataRefresh } from "../services/refreshStore";

const NAV_ITEMS = [
  { segment: "", label: "Dashboard", icon: LayoutDashboard, end: true },
  { segment: "holdings", label: "Holdings", icon: FileText },
  { segment: "performance", label: "Performance", icon: TrendingUp },
  { segment: "settings", label: "Settings", icon: Settings }
];

function Sidebar({ portfolioId }) {
  const navigate = useNavigate();
  const refreshKey = useDataRefresh();
  const [availablePortfolios, setAvailablePortfolios] = useState([]);

  useEffect(() => {
    let isMounted = true;

    const loadPortfolios = async () => {
      try {
        const result = await getPortfolios();

        if (!result.response.ok) {
          return;
        }

        const list = Array.isArray(result.data)
          ? result.data
          : [];

        if (isMounted) {
          setAvailablePortfolios(list);
        }
      } catch {
        if (isMounted) {
          setAvailablePortfolios([]);
        }
      }
    };

    loadPortfolios();

    return () => {
      isMounted = false;
    };
  }, [refreshKey]);

  const dropdownPortfolios =
    availablePortfolios.length > 0
      ? availablePortfolios
      : [
          {
            portfolio_id: portfolioId,
            portfolio_name: `Portfolio ${portfolioId}`,
          },
        ];

  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <span className="logo-green">Port</span><span className="logo-red">folio</span>
      </div>

      <div className="sidebar-portfolio-picker">
        <label htmlFor="sidebarPortfolioSwitcher">
          Portfolio
        </label>

        <select
          id="sidebarPortfolioSwitcher"
          value={portfolioId}
          onChange={(event) => {
            const nextPortfolioId = Number.parseInt(
              event.target.value,
              10
            );

            if (
              Number.isInteger(nextPortfolioId) &&
              nextPortfolioId > 0 &&
              nextPortfolioId !== portfolioId
            ) {
              navigate(`/portfolios/${nextPortfolioId}`);
            }
          }}
        >
          {dropdownPortfolios.map((portfolio) => (
            <option
              key={portfolio.portfolio_id}
              value={portfolio.portfolio_id}
            >
              {portfolio.portfolio_name ||
                `Portfolio ${portfolio.portfolio_id}`}
            </option>
          ))}
        </select>
      </div>

      {NAV_ITEMS.map(({ segment, label, icon: Icon, end }) => (
        <NavLink
          key={segment || "dashboard"}
          to={segment
            ? `/portfolios/${portfolioId}/${segment}`
            : `/portfolios/${portfolioId}`}
          end={end}
          className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
        >
          <Icon size={18} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

export default Sidebar;
