import { Routes, Route, Navigate } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";

import ScrollToTop from "./components/ScrollToTop";
import PageProject from "./pages/PageProject"
const App = () => {

  return (
    <ScrollToTop>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<PageProject />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ScrollToTop>
  );
};

export default App;
