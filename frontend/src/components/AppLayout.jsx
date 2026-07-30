import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import HeaderWithModal from "./HeaderWithModal";

function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />

      <div className="app-content">
        <HeaderWithModal />

        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
