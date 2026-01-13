import { Routes, Route } from "react-router-dom";

import LandingPage from "./pages/LandingPage";
import ScannerPage from "./pages/ScannerPage";
import ResultsPage from "./pages/ResultsPage";
import ServicesPage from "./pages/ServicesPage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import LegalPage from "./pages/LegalPage";

const App = () => {
  return (
    <>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/scanner" element={<ScannerPage />} />
        <Route path="/results/:assessmentId" element={<ResultsPage />} />
        <Route path="/services" element={<ServicesPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/legal" element={<LegalPage />} />
      </Routes>
    </>
  );
};

export default App;
