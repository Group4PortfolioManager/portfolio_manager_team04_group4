import { Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import AppLayout from "./components/AppLayout";
import Dashboard from "./pages/Dashboard";
import Holdings from "./pages/Holdings";
import Performance from "./pages/Performance";
import Settings from "./pages/Settings";

function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to="/portfolios/1" replace />}
      />

      <Route path="/portfolios/:portfolioId" element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="holdings" element={<Holdings />} />
        <Route path="performance" element={<Performance />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      <Route
        path="*"
        element={<Navigate to="/portfolios/1" replace />}
      />
    </Routes>
  );
}

export default App;
