import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";

type Question = {
  id: number;
  text: string;
  dimension_code: string;
  icon: string;
};

const mockQuestions: Question[] = [
  {
    id: 1,
    text: "We have documented processes for key operations.",
    dimension_code: "OPS",
    icon: "📑",
  },
  {
    id: 2,
    text: "We regularly measure customer satisfaction (NPS/CSAT).",
    dimension_code: "CX",
    icon: "🤝",
  },
  {
    id: 3,
    text: "We track key KPIs with up-to-date dashboards.",
    dimension_code: "DATA",
    icon: "📊",
  },
  {
    id: 4,
    text: "Roles & responsibilities for decisions are clearly defined.",
    dimension_code: "GOV",
    icon: "🛡️",
  },
];

const ScannerPage = () => {
  const navigate = useNavigate();
  const [orgName, setOrgName] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentQuestion = mockQuestions[currentIndex];
  const total = mockQuestions.length;
  const progress = Math.round(((currentIndex + 1) / total) * 100);

  const handleAnswerChange = (value: number) => {
    setAnswers((prev) => ({ ...prev, [currentQuestion.id]: value }));
    setError(null);
  };

  const handleNext = () => {
    if (!answers[currentQuestion.id]) {
      setError("Please choose a score from 1-5 before continuing.");
      return;
    }
    if (currentIndex < total - 1) {
      setCurrentIndex((i) => i + 1);
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex((i) => i - 1);
    }
  };

  const handleSubmit = async () => {
    const unanswered = mockQuestions.find((q) => !answers[q.id]);
    if (unanswered) {
      setError("Please answer all questions before finishing.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const createRes = await api.post("/assessments/", {
        organization_name: orgName || "Unknown Organization",
      });
      const assessmentId = createRes.data.id;

      const payload = Object.entries(answers).map(([questionId, val]) => ({
        question_id: Number(questionId),
        numeric_value: (Number(val) - 1) / 4,
        raw_value: String(val),
      }));

      await api.post(`/assessments/${assessmentId}/answers`, payload);
      const submitRes = await api.post(`/assessments/${assessmentId}/submit`);
      navigate(`/results/${submitRes.data.id}`);
    } catch (err) {
      console.error(err);
      setError("We couldn’t finish the scan. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="scanner" style={{ maxWidth: 680, margin: "0 auto", padding: "24px" }}>
      <h2 style={{ marginBottom: 8 }}>TekraQual Readiness Scan</h2>
      <p style={{ marginTop: 0, color: "#555" }}>
        Answer four quick questions (1 = not in place, 5 = excellent). Your
        responses stay private and generate a readiness summary.
      </p>

      <div className="org-name" style={{ marginBottom: 16 }}>
        <label style={{ fontWeight: 600 }}>Organization name</label>
        <input
          type="text"
          value={orgName}
          onChange={(e) => setOrgName(e.target.value)}
          placeholder="Acme Corp"
          style={{ width: "100%", padding: "8px", marginTop: 6 }}
        />
      </div>

      <div className="contact-inline" style={{ marginBottom: 16, fontSize: 14, color: "#444" }}>
        <strong>Questions?</strong> Email <strong>hello@tekraqual.com</strong> or <strong>support@tekraqual.com</strong> and we’ll help you interpret your results.
      </div>

      <div className="progress-bar" style={{ background: "#eee", height: 8, borderRadius: 6 }}>
        <div
          className="progress"
          style={{ width: `${progress}%`, height: "100%", background: "#0b8efb", borderRadius: 6 }}
        />
      </div>
      <p style={{ marginTop: 6, fontSize: 12, color: "#555" }}>
        Question {currentIndex + 1} of {total}
      </p>

      <div className="question" style={{ marginTop: 12, padding: "12px 0" }}>
        <p style={{ fontSize: 16, display: "flex", alignItems: "center", gap: 8 }}>
          <span>{currentQuestion.icon}</span>
          <strong>{currentQuestion.text}</strong>
        </p>
        <div className="likert" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {[1, 2, 3, 4, 5].map((val) => (
            <button
              key={val}
              className={answers[currentQuestion.id] === val ? "selected" : ""}
              onClick={() => handleAnswerChange(val)}
              style={{
                padding: "10px 12px",
                borderRadius: 6,
                border: answers[currentQuestion.id] === val ? "2px solid #0b8efb" : "1px solid #ccc",
                background: answers[currentQuestion.id] === val ? "#e8f3ff" : "#fff",
                minWidth: 48,
              }}
            >
              {val}
            </button>
          ))}
        </div>
        <p style={{ fontSize: 12, color: "#666", marginTop: 8 }}>
          1 = Not in place, 3 = Partially in place, 5 = Strong and consistent.
        </p>
      </div>

      <div className="scanner-actions" style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <button disabled={currentIndex === 0} onClick={handlePrev} style={{ padding: "10px 14px" }}>
          Back
        </button>
        {currentIndex < total - 1 ? (
          <button onClick={handleNext} style={{ padding: "10px 14px" }}>
            Next
          </button>
        ) : (
          <button onClick={handleSubmit} disabled={loading} style={{ padding: "10px 14px" }}>
            {loading ? "Calculating..." : "Finish & View Results"}
          </button>
        )}
      </div>

      {error && <p className="error" style={{ color: "#c00", marginTop: 12 }}>{error}</p>}
    </div>
  );
};

export default ScannerPage;
