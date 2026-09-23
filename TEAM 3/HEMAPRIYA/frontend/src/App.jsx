import { useEffect, useState } from "react";
import Select from "react-select";
import "./App.css";
import bmwCar from "./assets/bmw-car.png";

// Fallback data so the dashboard looks populated before the user
// generates a real recommendation (matches the reference design).
const demoResult = {
  Dealer: "D001 (Chennai)",
  Model: "3 Series",
  "Predicted Next Month Demand": 42,
  "Current Inventory": 28,
  "Target Inventory": 36,
  "Recommended Quantity": 36,
  "Days of Inventory": 24,
  "Sales Trend": "Upward",
  Reason:
    "Demand for BMW 3 Series is trending upward, while current inventory is below the target level. Increasing stock by 8 units will help meet upcoming demand and avoid stockouts.",
};

function LineChart({ history, loading }) {
  const width = 760;
  const height = 260;
  const padding = { top: 20, right: 20, bottom: 30, left: 34 };
  const chartMonths = history?.months || [];
  const actualSales = history?.actual_sales || [];
  const predictedDemand = history?.predicted_demand || [];
  const maxValue = Math.max(...actualSales, ...predictedDemand, 1);
  const maxY = Math.ceil(maxValue / 10) * 10;

  const xStep = chartMonths.length > 1
    ? (width - padding.left - padding.right) / (chartMonths.length - 1)
    : 0;
  const yScale = (val) =>
    height - padding.bottom - (val / maxY) * (height - padding.top - padding.bottom);
  const xScale = (i) => padding.left + i * xStep;

  const toPath = (data) =>
    data.map((v, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(v)}`).join(" ");

  const yTicks = Array.from({ length: 5 }, (_, index) => Math.round((maxY / 4) * index));

  if (loading) {
    return <div className="chart-state">Updating forecast...</div>;
  }

  if (!history || chartMonths.length === 0) {
    return <div className="chart-state">Select a dealer and model to view the forecast.</div>;
  }

  return (
    <svg viewBox={`0 0 ${width} ${height}`} width="100%" height={height} role="img" aria-label="Sales trend and demand forecast chart">
      {/* Y axis grid + labels */}
      {yTicks.map((t) => (
        <g key={t}>
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={yScale(t)}
            y2={yScale(t)}
            stroke="#eef2f7"
            strokeWidth="1"
          />
          <text x={padding.left - 10} y={yScale(t) + 4} textAnchor="end" fontSize="11" fill="#93a1b0">
            {t}
          </text>
        </g>
      ))}

      {/* X axis labels */}
      {chartMonths.map((m, i) => (
        <text key={m} x={xScale(i)} y={height - 8} textAnchor="middle" fontSize="11" fill="#93a1b0">
          {m}
        </text>
      ))}

      {/* Area under actual sales */}
      <path
        d={`${toPath(actualSales)} L ${xScale(actualSales.length - 1)} ${yScale(0)} L ${xScale(0)} ${yScale(0)} Z`}
        fill="rgba(23, 105, 209, 0.08)"
        stroke="none"
      />

      {/* Predicted demand (dashed) */}
      <path d={toPath(predictedDemand)} fill="none" stroke="#9b6bf0" strokeWidth="2" strokeDasharray="6 5" />
      {predictedDemand.map((v, i) => (
        <circle key={i} cx={xScale(i)} cy={yScale(v)} r="3.5" fill="#9b6bf0" />
      ))}

      {/* Actual sales (solid) */}
      <path d={toPath(actualSales)} fill="none" stroke="#1769d1" strokeWidth="2.5" />
      {actualSales.map((v, i) => (
        <circle key={i} cx={xScale(i)} cy={yScale(v)} r="3.5" fill="#1769d1" />
      ))}
    </svg>
  );
}

function App() {
  // ============================================================
  // DEALERS AND MODELS
  // ============================================================

  const [dealers, setDealers] = useState([]);
  const [models, setModels] = useState([]);

  const [dealer, setDealer] = useState("");
  const [model, setModel] = useState("");

  // ============================================================
  // APPLICATION STATE
  // ============================================================

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [error, setError] = useState("");
  const [history, setHistory] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Show real result once generated, otherwise fall back to demo data
  // so the dashboard matches the reference design on first load.
  const displayResult = result || demoResult;

  // ============================================================
  // LOAD DEALERS AND MODELS FROM FASTAPI
  // ============================================================

  useEffect(() => {
    const loadOptions = async () => {
      try {
        setOptionsLoading(true);
        setError("");

        const response = await fetch("http://127.0.0.1:8000/options");

        if (!response.ok) {
          throw new Error("Unable to load dealer and BMW model options.");
        }

        const data = await response.json();

        setDealers(data.dealers || []);
        setModels(data.models || []);

        if (data.dealers && data.dealers.length > 0) {
          setDealer(data.dealers[0]);
        }

        if (data.models && data.models.length > 0) {
          setModel(data.models[0]);
        }
      } catch (err) {
        console.error("Options loading error:", err);
        setError(
          "Unable to load dealers and BMW models. " +
            "Please make sure the FastAPI backend is running on port 8000."
        );
      } finally {
        setOptionsLoading(false);
      }
    };

    loadOptions();
  }, []);

  useEffect(() => {
    if (!dealer || !model) {
      setHistory(null);
      setHistoryLoading(false);
      return undefined;
    }

    const controller = new AbortController();

    const loadHistory = async () => {
      try {
        setHistoryLoading(true);
        const params = new URLSearchParams({ dealer_id: dealer, model });
        const response = await fetch(`http://127.0.0.1:8000/history?${params}`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Unable to load forecast history.");
        }

        setHistory(await response.json());
      } catch (err) {
        if (err.name !== "AbortError") {
          console.error("History loading error:", err);
          setHistory(null);
        }
      } finally {
        if (!controller.signal.aborted) {
          setHistoryLoading(false);
        }
      }
    };

    loadHistory();
    return () => controller.abort();
  }, [dealer, model]);

  // ============================================================
  // GET INVENTORY RECOMMENDATION
  // ============================================================

  const getRecommendation = async () => {
    if (!dealer || !model) {
      setError("Please select a dealer and BMW model.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dealer_id: dealer, model: model }),
      });

      if (!response.ok) {
        let errorMessage = "Unable to get recommendation.";
        try {
          const errorData = await response.json();
          if (errorData.detail) errorMessage = errorData.detail;
        } catch {
          // Ignore JSON parsing error
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Recommendation error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // REACT-SELECT OPTIONS
  // ============================================================

  const dealerOptions = dealers.map((dealerId) => ({ value: dealerId, label: dealerId }));
  const modelOptions = models.map((modelName) => ({ value: modelName, label: modelName }));

  const selectedDealer = dealerOptions.find((o) => o.value === dealer) || null;
  const selectedModel = modelOptions.find((o) => o.value === model) || null;

  const selectStyles = {
    control: (base, state) => ({
      ...base,
      minHeight: "54px",
      borderRadius: "9px",
      borderColor: state.isFocused ? "#0872d9" : "#d5e0eb",
      boxShadow: state.isFocused ? "0 0 0 3px rgba(8, 114, 217, 0.1)" : "none",
      "&:hover": { borderColor: "#b9cadb" },
      fontSize: "14px",
      cursor: "pointer",
    }),
    menu: (base) => ({ ...base, zIndex: 1000, borderRadius: "8px", overflow: "hidden" }),
    option: (base, state) => ({
      ...base,
      padding: "11px 14px",
      fontSize: "14px",
      cursor: "pointer",
      backgroundColor: state.isSelected ? "#0872d9" : state.isFocused ? "#eef6ff" : "#ffffff",
      color: state.isSelected ? "#ffffff" : "#263b52",
    }),
    placeholder: (base) => ({ ...base, color: "#8a9bad" }),
    singleValue: (base) => ({ ...base, color: "#263b52", fontWeight: 500 }),
  };

  // ============================================================
  // APPLICATION UI
  // ============================================================

  return (
    <div className="app">
      {/* ================= SIDEBAR ================= */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <img className="bmw-logo" src="/bmw-logo.svg" alt="BMW" />
          <div className="brand-name">BMW</div>
        </div>

        <nav className="navigation">
          <div className="nav-item">
            <span className="nav-icon">⌂</span>
            <span>Home</span>
          </div>

          <div className="nav-item active">
            <span className="nav-icon">📈</span>
            <span>Inventory Recommendation</span>
          </div>

          <div className="nav-item">
            <span className="nav-icon">📊</span>
            <span>Analytics</span>
          </div>

          <div className="nav-item">
            <span className="nav-icon">ⓘ</span>
            <span>About</span>
          </div>

          <div className="nav-item">
            <span className="nav-icon">?</span>
            <span>Help</span>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className="footer-line"></div>
          <span>Sheer Driving Pleasure</span>
        </div>
      </aside>

      {/* ================= MAIN ================= */}
      <main className="main-content">
        {/* TOPBAR */}
        <header className="topbar">
          <div className="topbar-title">Dealer Analytics</div>

          <div className="topbar-right">
            <div className="topbar-brand">
              <img className="mini-bmw-logo" src="/bmw-logo.svg" alt="BMW" />
              <span>BMW</span>
            </div>

            <div className="topbar-user">
              <span className="user-icon">👤</span>
              <span>Welcome</span>
              <span className="chevron">⌄</span>
            </div>
          </div>
        </header>

        {/* HERO */}
        <section className="hero">
          <div className="hero-content">
            <h1>
              Dealer Inventory
              <br />
              Recommendation
            </h1>
            <p>
              Predict demand and recommend the right inventory for each
              dealer and BMW model using machine learning.
            </p>
          </div>

          <div className="hero-visual">
            <div className="hero-car">
              <img src={bmwCar} alt="BMW vehicle" />
            </div>

            <div className="hero-badge">
              <div className="hero-roundel">
                <img className="bmw-logo" src="/bmw-logo.svg" alt="BMW" />
              </div>
              <div className="hero-tagline">
                Smarter Inventory.
                <br />
                Stronger Sales.
              </div>
            </div>
          </div>
        </section>

        {/* DASHBOARD */}
        <div className="dashboard-grid">
          <div className="dashboard-left">
            {/* SELECT DETAILS */}
            <section className="select-card">
              <div className="card-heading">
                <div className="heading-icon">📍</div>
                <h2>Select Details</h2>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>
                    <span className="label-icon">📍</span> Dealer
                  </label>

                  <div className="select-wrapper">
                    <Select
                      options={dealerOptions}
                      value={selectedDealer}
                      onChange={(selected) => {
                        setDealer(selected ? selected.value : "");
                        setHistory(null);
                        setHistoryLoading(Boolean(selected && model));
                        setResult(null);
                        setError("");
                      }}
                      placeholder={optionsLoading ? "Loading dealers..." : "Choose a dealer"}
                      isSearchable
                      isClearable
                      isDisabled={optionsLoading || loading}
                      styles={selectStyles}
                      noOptionsMessage={() => "No dealer found"}
                    />
                  </div>

                  {!optionsLoading && (
                    <small className="selector-hint">{dealers.length} dealers available</small>
                  )}
                </div>

                <div className="form-group">
                  <label>
                    <span className="label-icon">🚗</span> BMW Model
                  </label>

                  <div className="select-wrapper">
                    <Select
                      options={modelOptions}
                      value={selectedModel}
                      onChange={(selected) => {
                        setModel(selected ? selected.value : "");
                        setHistory(null);
                        setHistoryLoading(Boolean(selected && dealer));
                        setResult(null);
                        setError("");
                      }}
                      placeholder={optionsLoading ? "Loading models..." : "Choose a BMW model"}
                      isSearchable
                      isClearable
                      isDisabled={optionsLoading || loading}
                      styles={selectStyles}
                      noOptionsMessage={() => "No BMW model found"}
                    />
                  </div>

                  {!optionsLoading && (
                    <small className="selector-hint">{models.length} BMW models available</small>
                  )}
                </div>

                <button
                  className="recommend-button"
                  onClick={getRecommendation}
                  disabled={loading || optionsLoading || !dealer || !model}
                >
                  <span>✨</span>
                  {optionsLoading
                    ? "Loading Options..."
                    : loading
                    ? "Generating..."
                    : "Generate Recommendation"}
                  <span>→</span>
                </button>
              </div>
            </section>

            {/* ERROR */}
            {error && (
              <div className="error-box">
                <strong>Unable to process request</strong>
                <p>{error}</p>
                <small>Make sure the FastAPI backend is running on port 8000.</small>
              </div>
            )}

            {/* METRIC CARDS */}
            <div className="metric-grid">
              <div className="metric-card demand">
                <div className="metric-icon">📈</div>
                <span className="metric-label">Predicted Demand</span>
                <div className="metric-value">
                  {Number(displayResult["Predicted Next Month Demand"]).toFixed(0)}
                  <span>units</span>
                </div>
                <small className="metric-delta">↑ 12% vs last month</small>
              </div>

              <div className="metric-card inventory">
                <div className="metric-icon">📦</div>
                <span className="metric-label">Current Inventory</span>
                <div className="metric-value">
                  {Number(displayResult["Current Inventory"]).toFixed(0)}
                  <span>units</span>
                </div>
                <small className="metric-delta">↑ 5% vs last month</small>
              </div>

              <div className="metric-card quantity">
                <div className="metric-icon">🎯</div>
                <span className="metric-label">Recommended Quantity</span>
                <div className="metric-value">
                  {Number(displayResult["Recommended Quantity"]).toFixed(0)}
                  <span>units</span>
                </div>
                <small className="metric-delta">↑ 8% vs current stock</small>
              </div>

              <div className="metric-card days">
                <div className="metric-icon">📅</div>
                <span className="metric-label">Days of Inventory</span>
                <div className="metric-value">
                  {Number(displayResult["Days of Inventory"]).toFixed(0)}
                  <span>days</span>
                </div>
                <small className="metric-delta">↑ 6 days vs current</small>
              </div>
            </div>

            {/* CHART */}
            <section className="chart-card">
              <div className="chart-header">
                <div className="chart-title">
                  <div className="heading-icon">📈</div>
                  Sales Trend &amp; Demand Forecast
                </div>

                <div className="chart-legend">
                  <span>
                    <span className="legend-dot actual"></span> Actual Sales
                  </span>
                  <span>
                    <span className="legend-dot predicted"></span> Predicted Demand
                  </span>
                </div>
              </div>

              <LineChart history={history} loading={historyLoading} />
            </section>
          </div>

          {/* RECOMMENDATION SUMMARY */}
          <aside className="summary-card">
            <div className="summary-title">
              <div className="heading-icon">✔</div>
              Recommendation Summary
            </div>

            <div className="summary-vehicle">
              <div className="summary-vehicle-info">
                <img className="bmw-logo" src="/bmw-logo.svg" alt="BMW" />
                <div>
                  <h3>BMW {displayResult.Model}</h3>
                  <p>Dealer: {displayResult.Dealer}</p>
                </div>
              </div>
              <span className="badge-recommended">Recommended</span>
            </div>

            <div className="summary-list">
              <div className="summary-row">
                <span>Predicted Demand</span>
                <span>{Number(displayResult["Predicted Next Month Demand"]).toFixed(0)} units</span>
              </div>
              <div className="summary-row">
                <span>Current Inventory</span>
                <span>{Number(displayResult["Current Inventory"]).toFixed(0)} units</span>
              </div>
              <div className="summary-row">
                <span>Recommended Quantity</span>
                <span>{Number(displayResult["Recommended Quantity"]).toFixed(0)} units</span>
              </div>
              <div className="summary-row">
                <span>Stock to Add</span>
                <span>
                  +
                  {Math.max(
                    Number(displayResult["Recommended Quantity"]) -
                      Number(displayResult["Current Inventory"]),
                    0
                  ).toFixed(0)}{" "}
                  units
                </span>
              </div>
              <div className="summary-row">
                <span>Days of Inventory</span>
                <span>{Number(displayResult["Days of Inventory"]).toFixed(0)} days</span>
              </div>
            </div>

            <div className="why-box">
              <div className="why-box-title">💡 Why This Recommendation?</div>
              <p>{displayResult.Reason}</p>
            </div>
          </aside>
        </div>

        {/* FOOTER */}
        <footer className="page-footer">
          <span>© 2025 BMW. Dealer Inventory Recommendation.</span>
          <span>Built with ❤ for a smarter tomorrow.</span>
        </footer>
      </main>
    </div>
  );
}

export default App;