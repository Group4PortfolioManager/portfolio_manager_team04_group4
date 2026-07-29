import { NavLink } from "react-router-dom";
import { LayoutDashboard, FileText, TrendingUp, Settings, ChartCandlestick } from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/holdings", label: "Holdings", icon: FileText },
  { to: "/performance", label: "Performance", icon: TrendingUp },
  { to: "/settings", label: "Settings", icon: Settings }
];

function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-brand">
        <span className="logo-green">Port</span><span className="logo-red">folio</span>
      </div>

      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
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
