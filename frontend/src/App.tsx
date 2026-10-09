import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import CustomerSupportPage from "./pages/CustomerSupportPage";

import AdminDashboardPage from "./pages/AdminDashboardPage";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            <CustomerSupportPage />
          }
        />

        <Route
          path="/admin"
          element={
            <AdminDashboardPage />
          }
        />

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;