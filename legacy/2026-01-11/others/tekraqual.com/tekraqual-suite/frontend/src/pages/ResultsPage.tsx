import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";

// Readiness bands
const bands = [
  { min: 0, max: 49, label: "Foundation" },
  { min: 50, max: 64, label: "Bronze Potential" },
  { min: 65, max: 79, label: "Silver Potential" },
  { min: 80, max: 100, label: "Gold Potential" },
];

const ResultsPage = () => {
  const { assessmentId } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);   // assessment data
  const [report, setReport] = useState(null); // guidance report
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      if (!assessmentId) {
        setError("No assessment ID provided.");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const [assessmentRes, reportRes] = await Promise.all([
          api.get(`/assessments/${assessmentId}`),
          api.get(`/assessments/${assessmentId}/report`),
        ]);

        setData(assessmentRes.data);
        setReport(reportRes.data);
      } catch (e) {
        console.error(e);
        setError("Unable to load assessment report. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [assessmentId]);

  const calculateReadinessBand = (score) => {
    if (score == null) {
      return { label: "Unknown", gapToNext: null };
    }
    const clamped = Math.min(100, Math.max(0, score));
    const band = bands.find((b) => clamped >= b.min && clamped <= b.max) || bands[0];
    const nextBand = bands.find((b) => b.min > clamped);
    const gapToNext = nextBand ? Math.max(0, nextBand.min - clamped) : null;
    return { label: band.label, gapToNext };
  };

  if (loading) {
    return (
      <div style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
        <p>Loading TekraQual results…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
        <p style={{ color: "red" }}>{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
        <p>Assessment not found.</p>
      </div>
    );
  }

  // --- from here, we KNOW data exists ---

  console.log("TekraQual assessment data:", data);
  console.log("TekraQual report data:", report);

  const overallScore = data.overall_score != null ? data.overall_score : 0;
  const overallBand = calculateReadinessBand(overallScore);

  const dimensionScores = Array.isArray(data.dimension_scores)
    ? data.dimension_scores
    : [];

  const strengths = report && Array.isArray(report.strengths) ? report.strengths : [];
  const focusAreas =
    report && Array.isArray(report.focus_areas) ? report.focus_areas : [];
  const next90 =
    report && Array.isArray(report.next_90_days) ? report.next_90_days : [];
  const offers =
    report && Array.isArray(report.recommended_offers)
      ? report.recommended_offers
      : [];

  const apiBase = import.meta.env.VITE_API_BASE_URL;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      {/* Header + actions */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <h2>TekraQual Results</h2>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={() => {
              if (!assessmentId) return;
              const url = `${apiBase}/assessments/${assessmentId}/report_html`;
              window.open(url, "_blank", "noopener,noreferrer");
            }}
            style={{
              padding: "8px 14px",
              borderRadius: 6,
              border: "1px solid #ccc",
              cursor: "pointer",
              background: "#fff",
              fontSize: 14,
            }}
          >
            Download / Print Report
          </button>
          <button
            onClick={() => navigate("/")}
            style={{
              padding: "8px 14px",
              borderRadius: 6,
              border: "1px solid #ccc",
              cursor: "pointer",
              background: "#f5f5f5",
              fontSize: 14,
            }}
          >
            New Scan
          </button>
        </div>
      </div>

      {/* Results content */}
      <div className="results" style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}>
        <h2>TekraQual Readiness Summary</h2>
        <p>
          <strong>Organization:</strong> {data.organization_name}
        </p>
        <p>
          <strong>Overall Score:</strong> {Math.round(overallScore)}/100{" · "}
          <strong>Level:</strong> {data.readiness_level || overallBand.label}
        </p>
        {overallBand.gapToNext !== null && (
          <p style={{ fontSize: 14, color: "#555" }}>
            You are approximately <strong>{overallBand.gapToNext}</strong> points away
            from the next readiness band.
          </p>
        )}

        <h3 style={{ marginTop: 24 }}>Dimension Scores</h3>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: 8,
            fontSize: 14,
          }}
        >
          <thead>
            <tr>
              <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>
                Dimension
              </th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>
                Code
              </th>
              <th style={{ textAlign: "right", borderBottom: "1px solid #ddd", padding: 8 }}>
                Score
              </th>
              <th style={{ textAlign: "left", borderBottom: "1px solid #ddd", padding: 8 }}>
                Level
              </th>
            </tr>
          </thead>
          <tbody>
            {dimensionScores.map((ds) => (
              <tr key={ds.dimension_code}>
                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>
                  {ds.dimension_name}
                </td>
                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>
                  {ds.dimension_code}
                </td>
                <td
                  style={{
                    padding: 8,
                    borderBottom: "1px solid #eee",
                    textAlign: "right",
                  }}
                >
                  {Math.round(ds.score)}
                </td>
                <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{ds.level}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {report && (
          <>
            <section style={{ marginTop: 24 }}>
              <h3>Summary</h3>
              <p>{report.summary}</p>
            </section>

            <section style={{ marginTop: 24 }}>
              <h3>Key Strengths</h3>
              <ul>
                {strengths.map((s, idx) => (
                  <li key={idx} style={{ marginBottom: 8 }}>
                    <strong>{s.title}</strong>
                    {s.score != null && s.band && (
                      <span style={{ marginLeft: 8, fontSize: 12, color: "#555" }}>
                        {Math.round(s.score)}/100 · {s.band}
                      </span>
                    )}
                    <div>{s.body}</div>
                  </li>
                ))}
              </ul>
            </section>

            <section style={{ marginTop: 24 }}>
              <h3>Priority Focus Areas</h3>
              <ul>
                {focusAreas.map((f, idx) => (
                  <li key={idx} style={{ marginBottom: 8 }}>
                    <strong>{f.title}</strong>
                    {f.score != null && f.band && (
                      <span style={{ marginLeft: 8, fontSize: 12, color: "#555" }}>
                        {Math.round(f.score)}/100 · {f.band}
                      </span>
                    )}
                    <div>{f.body}</div>
                  </li>
                ))}
              </ul>
            </section>

            <section style={{ marginTop: 24 }}>
              <h3>Next 90 Days – Suggested Actions</h3>
              <ol>
                {next90.map((n, idx) => (
                  <li key={idx} style={{ marginBottom: 8 }}>
                    <strong>{n.title}</strong>
                    <div>{n.body}</div>
                  </li>
                ))}
              </ol>
            </section>

            <section style={{ marginTop: 24 }}>
              <h3>Larry CoPilot – Starter Involvement</h3>
              <p>
                Based on your current TekraQual results, a basic Larry CoPilot setup can help
                by:
              </p>
              <ul>
                <li>Summarizing daily activity in your weakest readiness area.</li>
                <li>Drafting responses and checklists for repetitive tasks.</li>
                <li>Producing a short weekly recap against your 90-day priorities.</li>
              </ul>
              <p style={{ fontSize: 12, color: "#666" }}>
                This makes sure improvements don’t just stay on paper, but show up in your
                day-to-day operations.
              </p>
            </section>

            <section style={{ marginTop: 24 }}>
              <h3>How TekraQual & Larry Can Help Further</h3>
              <ul>
                {offers.map((r, idx) => (
                  <li key={idx} style={{ marginBottom: 8 }}>
                    <strong>{r.title}</strong>
                    <div>{r.body}</div>
                  </li>
                ))}
              </ul>
            </section>
          </>
        )}
      </div>
    </div>
  );
};

export default ResultsPage;
