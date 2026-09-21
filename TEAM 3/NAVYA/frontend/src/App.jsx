import { useEffect, useMemo, useState } from "react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
} from "recharts";

import "./App.css";


const API_BASE = "";


/* ============================================================
   COMPONENT
   ============================================================ */

function App() {

  const [summary, setSummary] = useState(null);
  const [models, setModels] = useState([]);
  const [regions, setRegions] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [dealers, setDealers] = useState([]);

  const [apiHealthy, setApiHealthy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const [selectedModel, setSelectedModel] = useState(null);
  const [selectedRegion, setSelectedRegion] = useState(null);


  /* ==========================================================
     LOAD DASHBOARD DATA
     ========================================================== */

  const loadDashboardData = async () => {

    setLoading(true);
    setError(null);

    try {

      const healthResponse = await fetch(
        `${API_BASE}/health`
      );

      if (!healthResponse.ok) {
        throw new Error(
          "FastAPI health check failed."
        );
      }

      setApiHealthy(true);


      const [
        summaryResponse,
        modelsResponse,
        regionsResponse,
        maintenanceResponse,
        dealersResponse,
      ] = await Promise.all([

        fetch(`${API_BASE}/api/kpis/summary`),

        fetch(`${API_BASE}/api/kpis/models`),

        fetch(`${API_BASE}/api/kpis/regions`),

        fetch(`${API_BASE}/api/kpis/maintenance`),

        fetch(`${API_BASE}/api/kpis/dealers`),

      ]);


      if (
        !summaryResponse.ok ||
        !modelsResponse.ok ||
        !regionsResponse.ok ||
        !maintenanceResponse.ok ||
        !dealersResponse.ok
      ) {

        throw new Error(
          "One or more dashboard APIs returned an error."
        );

      }


      const [
        summaryData,
        modelsData,
        regionsData,
        maintenanceData,
        dealersData,
      ] = await Promise.all([

        summaryResponse.json(),

        modelsResponse.json(),

        regionsResponse.json(),

        maintenanceResponse.json(),

        dealersResponse.json(),

      ]);


      setSummary(summaryData);
      setModels(modelsData);
      setRegions(regionsData);
      setMaintenance(maintenanceData);
      setDealers(dealersData);

      setLastUpdated(new Date());

    }

    catch (err) {

      console.error(err);

      setApiHealthy(false);

      setError(
        err.message ||
        "Unable to load dashboard data."
      );

    }

    finally {

      setLoading(false);

    }

  };


  /* ==========================================================
     INITIAL LOAD
     ========================================================== */

  useEffect(() => {

    loadDashboardData();

  }, []);


  /* ==========================================================
     FORMATTERS
     ========================================================== */

  const formatCurrency = (value) => {

    if (
      value === undefined ||
      value === null ||
      Number.isNaN(Number(value))
    ) {
      return "₹0";
    }

    return new Intl.NumberFormat(
      "en-IN",
      {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
      }
    ).format(value);

  };


  const formatNumber = (value) => {

    if (
      value === undefined ||
      value === null ||
      Number.isNaN(Number(value))
    ) {
      return "0";
    }

    return new Intl.NumberFormat(
      "en-IN"
    ).format(value);

  };


  /* ==========================================================
     FILTERED DATA
     ========================================================== */

  const filteredModels = useMemo(() => {

    if (!selectedModel) {
      return models;
    }

    return models.filter(
      (item) =>
        item.model === selectedModel
    );

  }, [models, selectedModel]);


  const filteredRegions = useMemo(() => {

    return regions.filter(
      (item) =>
        item.region &&
        item.region !== "Missing"
    );

  }, [regions]);


  const selectedModelData = models.find(
    (item) =>
      item.model === selectedModel
  );


  const selectedRegionData = regions.find(
    (item) =>
      item.region === selectedRegion
  );


  /* ==========================================================
     CHART COLORS
     ========================================================== */

  const regionColors = [
    "#1688ff",
    "#16b7ff",
    "#1ed6c5",
    "#596cff",
    "#8a63ff",
  ];


  /* ==========================================================
     PIPELINE
     ========================================================== */

  const pipelineStages = [

    {
      number: "01",
      name: "BMW Data",
      detail: "CSV Sources",
      icon: "▣",
    },

    {
      number: "02",
      name: "S3 Raw",
      detail: "Data Lake",
      icon: "☁",
    },

    {
      number: "03",
      name: "PySpark",
      detail: "Validation + ETL",
      icon: "ϟ",
      active: true,
    },

    {
      number: "04",
      name: "Parquet",
      detail: "Curated Data",
      icon: "▤",
    },

    {
      number: "05",
      name: "Athena",
      detail: "Analytics",
      icon: "⌕",
    },

    {
      number: "06",
      name: "FastAPI",
      detail: "Business API",
      icon: "◇",
      active: true,
    },

  ];


  /* ==========================================================
     CLEAR FILTERS
     ========================================================== */

  const clearFilters = () => {

    setSelectedModel(null);
    setSelectedRegion(null);

  };


  /* ==========================================================
     BAR CLICK
     ========================================================== */

  const handleModelClick = (data) => {

    const model =
      data?.model ||
      data?.payload?.model;

    if (model) {
      setSelectedModel(model);
    }

  };


  /* ==========================================================
     REGION CLICK
     ========================================================== */

  const handleRegionClick = (data) => {

    const region =
      data?.region ||
      data?.payload?.region;

    if (region) {
      setSelectedRegion(region);
    }

  };


  /* ==========================================================
     LOADING SCREEN
     ========================================================== */

  if (
    loading &&
    !summary
  ) {

    return (

      <div className="loading-screen">

        <div className="loading-logo">

          <img
            src="/assets/bmw-logo.svg"
            alt="BMW"
            className="loading-bmw-logo"
          />

        </div>

        <div className="loading-spinner"></div>

        <h2>
          Mobility Intelligence
        </h2>

        <p>
          Initializing enterprise data platform...
        </p>

      </div>

    );

  }


  /* ==========================================================
     DASHBOARD
     ========================================================== */

  return (

    <div className="app-shell">


      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="dashboard-header">

        <div className="brand-section">

          <div className="brand-mark">

            <img
              src="/assets/bmw-logo.svg"
              alt="BMW"
              className="bmw-logo"
            />

          </div>


          <div className="brand-text">

            <p className="eyebrow">
              ENTERPRISE DATA PLATFORM
            </p>

            <h1>
              Mobility Intelligence
            </h1>

            <p className="subtitle">
              Connected Mobility Batch ETL Analytics
            </p>

          </div>

        </div>


        <div className="header-actions">

          <div className="system-status">

            <span
              className={
                apiHealthy
                  ? "status-dot online"
                  : "status-dot offline"
              }
            />

            <span>
              {apiHealthy
                ? "API Online"
                : "API Offline"}
            </span>

          </div>


          <button
            className="refresh-button"
            onClick={loadDashboardData}
            disabled={loading}
          >

            <span className="refresh-icon">
              ↻
            </span>

            {loading
              ? "Refreshing..."
              : "Refresh Data"}

          </button>

        </div>

      </header>


      {/* ======================================================
          HERO
      ====================================================== */}

      <section className="hero-strip">

        <div className="hero-content">

          <span className="hero-kicker">
            BMW CONNECTED MOBILITY
          </span>

          <h2>
            From raw data to
            <span>
              {" "}business intelligence.
            </span>
          </h2>

          <p>
            An end-to-end enterprise batch ETL platform
            transforming BMW mobility data into actionable
            analytics.
          </p>

        </div>


        <div className="hero-meta">

          <div className="hero-meta-card">

            <span>
              PIPELINE
            </span>

            <strong>
              <i className="tiny-green-dot"></i>
              HEALTHY
            </strong>

          </div>


          <div className="hero-meta-card">

            <span>
              DATASETS
            </span>

            <strong>
              04
            </strong>

          </div>


          <div className="hero-meta-card">

            <span>
              ENGINE
            </span>

            <strong>
              PYSPARK
            </strong>

          </div>

        </div>

      </section>


      {/* ======================================================
          ERROR
      ====================================================== */}

      {error && (

        <div className="error-banner">

          <div>

            <strong>
              Data connection error
            </strong>

            <span>
              {error}
            </span>

          </div>

          <button
            onClick={loadDashboardData}
          >
            Retry
          </button>

        </div>

      )}


      {/* ======================================================
          FILTER BAR
      ====================================================== */}

      {(selectedModel || selectedRegion) && (

        <div className="filter-bar">

          <div className="filter-info">

            <span>
              ACTIVE FILTER
            </span>

            {selectedModel && (

              <strong>
                Model: {selectedModel}
              </strong>

            )}

            {selectedRegion && (

              <strong>
                Region: {selectedRegion}
              </strong>

            )}

          </div>


          <button
            onClick={clearFilters}
          >
            Clear filters ×
          </button>

        </div>

      )}


      {/* ======================================================
          KPI CARDS
      ====================================================== */}

      {summary && (

        <section className="kpi-grid">


          {/* REVENUE */}

          <div className="kpi-card primary">

            <div className="kpi-icon">
              ₹
            </div>

            <div className="kpi-content">

              <span className="kpi-label">
                TOTAL REVENUE
              </span>

              <strong className="kpi-value">
                {formatCurrency(
                  summary.total_revenue
                )}
              </strong>

              <span className="kpi-caption">
                Processed sales revenue
              </span>

            </div>

          </div>


          {/* VEHICLES */}

          <div className="kpi-card">

            <div className="kpi-icon">
              🚘
            </div>

            <div className="kpi-content">

              <span className="kpi-label">
                VEHICLES SOLD
              </span>

              <strong className="kpi-value">
                {formatNumber(
                  summary.total_vehicles_sold
                )}
              </strong>

              <span className="kpi-caption">
                Across processed sales
              </span>

            </div>

          </div>


          {/* RECORDS */}

          <div className="kpi-card">

            <div className="kpi-icon">
              ◈
            </div>

            <div className="kpi-content">

              <span className="kpi-label">
                CURATED RECORDS
              </span>

              <strong className="kpi-value">
                {formatNumber(
                  summary.total_sales_records
                )}
              </strong>

              <span className="kpi-caption">
                Validated sales records
              </span>

            </div>

          </div>


          {/* MAINTENANCE */}

          <div className="kpi-card">

            <div className="kpi-icon">
              ⚙
            </div>

            <div className="kpi-content">

              <span className="kpi-label">
                MAINTENANCE COST
              </span>

              <strong className="kpi-value">
                {formatCurrency(
                  summary.total_maintenance_cost
                )}
              </strong>

              <span className="kpi-caption">
                Processed service costs
              </span>

            </div>

          </div>

        </section>

      )}


      {/* ======================================================
          ANALYTICS GRID
      ====================================================== */}

      <section className="analytics-grid">


        {/* ====================================================
            MODEL REVENUE
        ===================================================== */}

        <div className="dashboard-card large">

          <div className="card-header">

            <div>

              <p className="card-eyebrow">
                SALES ANALYTICS
              </p>

              <h2>
                Revenue by BMW Model
              </h2>

              <span className="interactive-hint">
                Click a bar to inspect a model
              </span>

            </div>

            <span className="card-badge">
              {models.length} models
            </span>

          </div>


          <div className="chart-container model-chart">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <BarChart
                data={filteredModels}
                margin={{
                  top: 15,
                  right: 15,
                  left: 5,
                  bottom: 55,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                />

                <XAxis
                  dataKey="model"
                  angle={-25}
                  textAnchor="end"
                  interval={0}
                  height={60}
                />

                <YAxis
                  tickFormatter={(value) =>
                    `₹${(
                      value / 10000000
                    ).toFixed(1)}Cr`
                  }
                />

                <Tooltip
                  formatter={(value) =>
                    formatCurrency(value)
                  }
                />

                <Bar
                  dataKey="total_revenue"
                  name="Revenue"
                  radius={[
                    7,
                    7,
                    0,
                    0
                  ]}
                  onClick={handleModelClick}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>


          {selectedModelData && (

            <div className="insight-panel">

              <div>

                <span>
                  SELECTED MODEL
                </span>

                <strong>
                  {selectedModelData.model}
                </strong>

              </div>


              <div>

                <span>
                  VEHICLES SOLD
                </span>

                <strong>
                  {formatNumber(
                    selectedModelData.vehicles_sold
                  )}
                </strong>

              </div>


              <div>

                <span>
                  REVENUE
                </span>

                <strong>
                  {formatCurrency(
                    selectedModelData.total_revenue
                  )}
                </strong>

              </div>

            </div>

          )}

        </div>


        {/* ====================================================
            REGION REVENUE
        ===================================================== */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>

              <p className="card-eyebrow">
                GEOGRAPHY
              </p>

              <h2>
                Regional Revenue
              </h2>

              <span className="interactive-hint">
                Click a region to inspect
              </span>

            </div>

          </div>


          <div className="chart-container">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <PieChart>

                <Pie
                  data={filteredRegions}
                  dataKey="total_revenue"
                  nameKey="region"
                  cx="50%"
                  cy="48%"
                  outerRadius={105}
                  innerRadius={58}
                  paddingAngle={4}
                  onClick={handleRegionClick}
                >

                  {filteredRegions.map(
                    (entry, index) => (

                      <Cell
                        key={`cell-${index}`}
                        fill={
                          regionColors[
                            index %
                            regionColors.length
                          ]
                        }
                        opacity={
                          selectedRegion &&
                          selectedRegion !==
                            entry.region
                            ? 0.25
                            : 1
                        }
                      />

                    )
                  )}

                </Pie>


                <Tooltip
                  formatter={(value) =>
                    formatCurrency(value)
                  }
                />


                <Legend />

              </PieChart>

            </ResponsiveContainer>

          </div>


          {selectedRegionData && (

            <div className="region-insight">

              <span>
                SELECTED REGION
              </span>

              <strong>
                {selectedRegionData.region}
              </strong>

              <p>

                {formatNumber(
                  selectedRegionData.vehicles_sold
                )}

                {" "}vehicles ·{" "}

                {formatCurrency(
                  selectedRegionData.total_revenue
                )}

              </p>

            </div>

          )}

        </div>


        {/* ====================================================
            MAINTENANCE
        ===================================================== */}

        <div className="dashboard-card large">

          <div className="card-header">

            <div>

              <p className="card-eyebrow">
                AFTER-SALES INTELLIGENCE
              </p>

              <h2>
                Maintenance Cost by Service
              </h2>

            </div>


            <span className="card-badge">

              {summary
                ? formatNumber(
                    summary.total_maintenance_records
                  )
                : "0"}

              {" "}services

            </span>

          </div>


          <div className="chart-container">

            <ResponsiveContainer
              width="100%"
              height="100%"
            >

              <BarChart
                data={maintenance}
                layout="vertical"
                margin={{
                  top: 10,
                  right: 20,
                  left: 15,
                  bottom: 10,
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  horizontal={false}
                />

                <XAxis
                  type="number"
                  tickFormatter={(value) =>
                    `₹${(
                      value / 100000
                    ).toFixed(1)}L`
                  }
                />

                <YAxis
                  type="category"
                  dataKey="service_type"
                  width={105}
                />

                <Tooltip
                  formatter={(value) =>
                    formatCurrency(value)
                  }
                />

                <Bar
                  dataKey="total_maintenance_cost"
                  name="Maintenance Cost"
                  radius={[
                    0,
                    7,
                    7,
                    0
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>

        </div>


        {/* ====================================================
            TOP DEALERS
        ===================================================== */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>

              <p className="card-eyebrow">
                NETWORK PERFORMANCE
              </p>

              <h2>
                Top Dealers
              </h2>

            </div>

            <span className="card-badge">
              TOP 10
            </span>

          </div>


          <div className="dealer-list">

            {dealers.map(
              (dealer, index) => (

                <div
                  className="dealer-row"
                  key={
                    dealer.dealer_id
                  }
                >

                  <div className="dealer-rank">

                    {String(
                      index + 1
                    ).padStart(2, "0")}

                  </div>


                  <div className="dealer-info">

                    <strong>
                      {dealer.dealer_name}
                    </strong>

                    <span>
                      {dealer.city}
                      {" · "}
                      {dealer.region}
                    </span>

                  </div>


                  <div className="dealer-revenue">

                    <strong>
                      {formatCurrency(
                        dealer.total_revenue
                      )}
                    </strong>

                    <span>
                      {formatNumber(
                        dealer.vehicles_sold
                      )}
                      {" "}vehicles
                    </span>

                  </div>

                </div>

              )
            )}

          </div>

        </div>

      </section>


      {/* ======================================================
          DATA QUALITY + PIPELINE
      ====================================================== */}

      <section className="platform-grid">


        {/* ====================================================
            DATA QUALITY
        ===================================================== */}

        <div className="dashboard-card">

          <div className="card-header">

            <div>

              <p className="card-eyebrow">
                DATA GOVERNANCE
              </p>

              <h2>
                Data Quality Monitor
              </h2>

            </div>

            <span className="quality-badge">
              ● VALIDATED
            </span>

          </div>


          <div className="quality-list">


            <div className="quality-row">

              <span className="quality-icon">
                ✓
              </span>

              <div>

                <strong>
                  Schema Validation
                </strong>

                <small>
                  Explicit data types enforced
                </small>

              </div>

              <span className="quality-status">
                PASS
              </span>

            </div>


            <div className="quality-row">

              <span className="quality-icon">
                ✓
              </span>

              <div>

                <strong>
                  Null Handling
                </strong>

                <small>
                  Invalid records isolated
                </small>

              </div>

              <span className="quality-status">
                PASS
              </span>

            </div>


            <div className="quality-row">

              <span className="quality-icon">
                ✓
              </span>

              <div>

                <strong>
                  Duplicate Detection
                </strong>

                <small>
                  Business keys validated
                </small>

              </div>

              <span className="quality-status">
                PASS
              </span>

            </div>


            <div className="quality-row">

              <span className="quality-icon">
                ✓
              </span>

              <div>

                <strong>
                  Range & Date Checks
                </strong>

                <small>
                  Invalid values rejected
                </small>

              </div>

              <span className="quality-status">
                PASS
              </span>

            </div>

          </div>

        </div>


        {/* ====================================================
            PIPELINE
        ===================================================== */}

        <div className="dashboard-card pipeline-card">

          <div className="card-header">

            <div>

              <p className="card-eyebrow">
                DATA PLATFORM
              </p>

              <h2>
                Enterprise ETL Pipeline
              </h2>

            </div>

            <span className="live-badge">
              ● LIVE
            </span>

          </div>


          <div className="pipeline-flow">

            {pipelineStages.map(
              (stage, index) => (

                <div
                  className="pipeline-wrapper"
                  key={stage.number}
                >

                  <div
                    className={
                      stage.active
                        ? "pipeline-node active"
                        : "pipeline-node"
                    }
                  >

                    <span className="pipeline-icon">
                      {stage.icon}
                    </span>

                    <span className="pipeline-number">
                      {stage.number}
                    </span>

                    <strong>
                      {stage.name}
                    </strong>

                    <small>
                      {stage.detail}
                    </small>

                  </div>


                  {index <
                    pipelineStages.length - 1 && (

                    <div className="pipeline-arrow">
                      →
                    </div>

                  )}

                </div>

              )
            )}

          </div>

        </div>

      </section>


      {/* ======================================================
          PLATFORM SUMMARY
      ====================================================== */}

      <section className="platform-summary">


        <div>

          <span>
            PLATFORM STATUS
          </span>

          <strong>
            <i className="tiny-green-dot"></i>
            All systems operational
          </strong>

        </div>


        <div>

          <span>
            AWS REGION
          </span>

          <strong>
            eu-north-1
          </strong>

        </div>


        <div>

          <span>
            STORAGE
          </span>

          <strong>
            S3 + Parquet
          </strong>

        </div>


        <div>

          <span>
            QUERY ENGINE
          </span>

          <strong>
            Athena
          </strong>

        </div>


        <div>

          <span>
            API
          </span>

          <strong>
            FastAPI
          </strong>

        </div>

      </section>


      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer className="dashboard-footer">

        <div>

          <strong>
            BMW Enterprise Batch ETL
          </strong>

          <span>
            Connected Mobility Data Platform
          </span>

        </div>


        <div className="footer-right">

          <span>

            {lastUpdated
              ? `Last updated ${lastUpdated.toLocaleTimeString()}`
              : "Waiting for data"}

          </span>

          <span>
            AWS · PySpark · Parquet · Athena · FastAPI · React
          </span>

        </div>

      </footer>


    </div>

  );

}


export default App;