import { useNavigate } from "react-router-dom";

const LandingPage = () => {
  const navigate = useNavigate();

  const handleStartScan = () => navigate("/scanner");
  const handleBookCall = () => navigate("/contact");

  return (
    <div className="landing">
      <header className="hero">
        <h1>Turn Your Business Chaos into a Calm, AI-Powered Command Center</h1>
        <p>
          We set up Larry CoPilot and a TekraQual Readiness Scan so you get real
          automation, real insight, and real income faster.
        </p>
        <div className="hero-actions">
          <button onClick={handleStartScan}>Get Your Readiness Scan</button>
        </div>
      </header>
      <section className="contact-inline" style={{ marginTop: 24 }}>
        <h3>Need to talk first?</h3>
        <p style={{ margin: 0 }}>Email us at <strong>hello@tekraqual.com</strong> or <strong>support@tekraqual.com</strong>.</p>
        <p style={{ margin: 0 }}>We usually reply within one business day.</p>
      </section>
    </div>
  );
};

export default LandingPage;
