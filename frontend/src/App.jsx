import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  Boxes,
  BrainCircuit,
  Database,
  RefreshCw,
  TrendingUp,
} from "lucide-react";
import {
  Area,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  LineChart,
  Bar,
  BarChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { analyticsApi } from "./api";
import {
  formatNumber,
  formatPct,
  formatUsd,
  formatUsdFull,
} from "./format";

const chartColors = [
  "#22c55e",
  "#38bdf8",
  "#a78bfa",
  "#f59e0b",
  "#fb7185",
  "#2dd4bf",
  "#60a5fa",
  "#f472b6",
  "#84cc16",
  "#fb923c",
];

const modelLabels = {
  naive_last_value: "Último valor",
  linear_trend: "Tendencia lineal",
  holt_damped_trend: "Holt amortiguado",
};

function KpiCard({ icon: Icon, label, value, detail, positive }) {
  return (
    <article className="kpi-card">
      <div className="kpi-icon"><Icon size={20} /></div>
      <div>
        <span className="kpi-label">{label}</span>
        <strong className={positive === false ? "negative" : ""}>{value}</strong>
        <small>{detail}</small>
      </div>
    </article>
  );
}

function Panel({ title, subtitle, children, className = "" }) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-head">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
      </div>
      {children}
    </section>
  );
}

function App() {
  const [summary, setSummary] = useState(null);
  const [yearly, setYearly] = useState([]);
  const [growth, setGrowth] = useState([]);
  const [years, setYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState(null);
  const [topItems, setTopItems] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sectionLoading, setSectionLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadBase() {
    setLoading(true);
    setError("");

    try {
      const [
        summaryData,
        yearlyData,
        growthData,
        yearsData,
        forecastData,
      ] = await Promise.all([
        analyticsApi.summary(),
        analyticsApi.yearly(),
        analyticsApi.growth(),
        analyticsApi.years(),
        analyticsApi.forecast(3),
      ]);

      setSummary(summaryData);
      setYearly(yearlyData);
      setGrowth(growthData);
      setYears(yearsData.years);
      setForecast(forecastData);
      setSelectedYear((current) => current ?? summaryData.latest_year);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadBase();
  }, []);

  useEffect(() => {
    if (!selectedYear) return;

    let active = true;
    setSectionLoading(true);

    Promise.all([
      analyticsApi.topItems(selectedYear, 10),
      analyticsApi.chapters(selectedYear, 10),
    ])
      .then(([items, chapterRows]) => {
        if (!active) return;
        setTopItems(items);
        setChapters(chapterRows);
      })
      .catch((err) => {
        if (active) setError(err.message);
      })
      .finally(() => {
        if (active) setSectionLoading(false);
      });

    return () => {
      active = false;
    };
  }, [selectedYear]);

  const selectedGrowth = useMemo(
    () => growth.find((item) => item.year === selectedYear),
    [growth, selectedYear],
  );

  const forecastChartData = useMemo(() => {
    if (!forecast || !yearly.length) return [];

    const recentActual = yearly.slice(-8).map((row) => ({
      year: row.year,
      actual_usd: row.total_usd,
      predicted_usd: null,
      lower_usd: null,
      upper_usd: null,
    }));

    const lastActual = recentActual[recentActual.length - 1];

    return [
      ...recentActual,
      {
        ...lastActual,
        predicted_usd: lastActual.actual_usd,
        lower_usd: lastActual.actual_usd,
        upper_usd: lastActual.actual_usd,
      },
      ...forecast.forecast.map((point) => ({
        year: point.year,
        actual_usd: null,
        predicted_usd: point.predicted_usd,
        lower_usd: point.lower_usd,
        upper_usd: point.upper_usd,
      })),
    ];
  }, [forecast, yearly]);

  const nextForecast = forecast?.forecast?.[0];

  if (loading) {
    return (
      <main className="center-state">
        <RefreshCw className="spin" />
        Cargando dashboard...
      </main>
    );
  }

  if (error && !summary) {
    return (
      <main className="center-state error-state">
        <Database size={32} />
        <h1>No se pudo conectar con Analytics API</h1>
        <p>{error}</p>
        <button onClick={loadBase}>Reintentar</button>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <div className="eyebrow">
            <Activity size={15} />
            PORTFOLIO DATA PROJECT
          </div>
          <h1>Guatemala Export Analytics</h1>
          <p>
            Comercio General · Exportaciones por inciso arancelario · 2002–2025
          </p>
        </div>

        <div className="header-controls">
          <label>
            Año analizado
            <select
              value={selectedYear ?? ""}
              onChange={(event) =>
                setSelectedYear(Number(event.target.value))
              }
            >
              {years.map((year) => (
                <option value={year} key={year}>{year}</option>
              ))}
            </select>
          </label>

          <span className="status"><i /> API conectada</span>
        </div>
      </header>

      {error && <div className="inline-error">{error}</div>}

      <section className="kpi-grid">
        <KpiCard
          icon={TrendingUp}
          label={`Exportaciones ${selectedYear}`}
          value={formatUsd(selectedGrowth?.total_usd)}
          detail={
            selectedGrowth?.is_provisional
              ? "Cifra provisional"
              : "Cifra oficial del dataset"
          }
        />
        <KpiCard
          icon={BarChart3}
          label="Crecimiento interanual"
          value={formatPct(selectedGrowth?.growth_pct)}
          detail={
            selectedGrowth?.previous_year_total_usd
              ? `vs. ${selectedYear - 1}`
              : "Sin año previo disponible"
          }
          positive={
            selectedGrowth?.growth_pct == null ||
            selectedGrowth.growth_pct >= 0
          }
        />
        <KpiCard
          icon={Boxes}
          label="Incisos arancelarios"
          value={formatNumber(summary.tariff_items)}
          detail="Códigos únicos en la serie"
        />
        <KpiCard
          icon={Database}
          label="Observaciones"
          value={formatNumber(summary.observations)}
          detail={`${summary.first_year}–${summary.latest_year}`}
        />
      </section>

      <section className="dashboard-grid wide-left">
        <Panel
          title="Evolución histórica"
          subtitle="Valor total anual de exportaciones en USD"
        >
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={yearly}
                margin={{ top: 10, right: 15, left: 0, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#253044"
                />
                <XAxis
                  dataKey="year"
                  tick={{ fill: "#94a3b8", fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tickFormatter={formatUsd}
                  tick={{ fill: "#94a3b8", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  width={74}
                />
                <Tooltip
                  formatter={(value) => formatUsdFull(value)}
                  labelFormatter={(value) => `Año ${value}`}
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #334155",
                    borderRadius: 10,
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="total_usd"
                  stroke="#22c55e"
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel
          title="Variación anual"
          subtitle="Crecimiento porcentual respecto al año anterior"
        >
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={growth.filter((row) => row.growth_pct !== null)}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#253044"
                />
                <XAxis
                  dataKey="year"
                  tick={{ fill: "#94a3b8", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tickFormatter={(value) => `${value}%`}
                  tick={{ fill: "#94a3b8", fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  formatter={(value) => `${Number(value).toFixed(2)}%`}
                  contentStyle={{
                    background: "#111827",
                    border: "1px solid #334155",
                    borderRadius: 10,
                  }}
                />
                <Bar
                  dataKey="growth_pct"
                  radius={[4, 4, 0, 0]}
                  fill="#38bdf8"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </section>

      <section className="dashboard-grid">
        <Panel
          title={`Top incisos · ${selectedYear}`}
          subtitle="Mayores valores exportados por código arancelario"
        >
          {sectionLoading ? (
            <div className="panel-loading">Actualizando...</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Inciso / producto</th>
                    <th>Cap.</th>
                    <th>Valor</th>
                    <th>Part.</th>
                  </tr>
                </thead>
                <tbody>
                  {topItems.map((item) => (
                    <tr key={item.code}>
                      <td>{item.rank}</td>
                      <td>
                        <div className="item-cell">
                          <code>{item.code}</code>
                          <span
                            className={
                              item.description
                                ? "item-description"
                                : "item-description missing"
                            }
                            title={item.description ?? ""}
                          >
                            {item.description || "Sin descripción SAC"}
                          </span>
                        </div>
                      </td>
                      <td>{item.chapter}</td>
                      <td>{formatUsdFull(item.value_usd)}</td>
                      <td>{item.share_pct.toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>

        <Panel
          title={`Principales capítulos · ${selectedYear}`}
          subtitle="Participación de los 10 capítulos con mayor valor"
        >
          <div className="chapter-layout">
            <div className="donut">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chapters}
                    dataKey="total_usd"
                    nameKey="chapter"
                    innerRadius={58}
                    outerRadius={90}
                    paddingAngle={2}
                  >
                    {chapters.map((entry, index) => (
                      <Cell
                        key={entry.chapter}
                        fill={chartColors[index % chartColors.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => formatUsdFull(value)}
                    labelFormatter={(label) => `Capítulo ${label}`}
                    contentStyle={{
                      background: "#111827",
                      border: "1px solid #334155",
                      borderRadius: 10,
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chapter-list">
              {chapters.map((chapter, index) => (
                <div key={chapter.chapter}>
                  <span>
                    <i
                      style={{
                        background: chartColors[index % chartColors.length],
                      }}
                    />
                    <b>Cap. {chapter.chapter}</b>
                    <em title={chapter.description ?? ""}>
                      {chapter.description || "Sin descripción"}
                    </em>
                  </span>
                  <strong>{chapter.share_pct.toFixed(2)}%</strong>
                </div>
              ))}
            </div>
          </div>
        </Panel>
      </section>

      <section className="forecast-section">
        <Panel
          className="forecast-panel"
          title="Forecast de exportaciones"
          subtitle="Proyección anual · selección automática mediante backtesting"
        >
          <div className="forecast-layout">
            <div className="forecast-chart">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart
                  data={forecastChartData}
                  margin={{ top: 10, right: 18, left: 0, bottom: 0 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    vertical={false}
                    stroke="#253044"
                  />
                  <XAxis
                    dataKey="year"
                    tick={{ fill: "#94a3b8", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tickFormatter={formatUsd}
                    tick={{ fill: "#94a3b8", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                    width={76}
                  />
                  <Tooltip
                    formatter={(value, name) => {
                      const labels = {
                        actual_usd: "Real",
                        predicted_usd: "Forecast",
                        lower_usd: "Límite inferior",
                        upper_usd: "Límite superior",
                      };
                      return [formatUsdFull(value), labels[name] || name];
                    }}
                    labelFormatter={(value) => `Año ${value}`}
                    contentStyle={{
                      background: "#111827",
                      border: "1px solid #334155",
                      borderRadius: 10,
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="upper_usd"
                    stroke="none"
                    fill="#8b5cf6"
                    fillOpacity={0.10}
                    connectNulls={false}
                  />
                  <Area
                    type="monotone"
                    dataKey="lower_usd"
                    stroke="none"
                    fill="#08111f"
                    fillOpacity={1}
                    connectNulls={false}
                  />

                  <Line
                    type="monotone"
                    dataKey="actual_usd"
                    stroke="#22c55e"
                    strokeWidth={3}
                    dot={false}
                    connectNulls={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="predicted_usd"
                    stroke="#a78bfa"
                    strokeWidth={3}
                    strokeDasharray="7 6"
                    dot={{ r: 4, fill: "#a78bfa" }}
                    connectNulls={false}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>

            <aside className="forecast-summary">
              <div className="forecast-badge">
                <BrainCircuit size={17} />
                Modelo seleccionado
              </div>

              <strong className="forecast-model">
                {modelLabels[forecast?.selected_model] || forecast?.selected_model}
              </strong>

              {nextForecast && (
                <div className="forecast-next">
                  <span>Estimación {nextForecast.year}</span>
                  <strong>{formatUsd(nextForecast.predicted_usd)}</strong>
                  <small>
                    Rango aprox. {formatUsd(nextForecast.lower_usd)} –{" "}
                    {formatUsd(nextForecast.upper_usd)}
                  </small>
                </div>
              )}

              <div className="forecast-metrics">
                <div>
                  <span>MAE backtest</span>
                  <strong>{formatUsd(forecast?.mae)}</strong>
                </div>
                <div>
                  <span>RMSE backtest</span>
                  <strong>{formatUsd(forecast?.rmse)}</strong>
                </div>
                <div>
                  <span>Validación</span>
                  <strong>{forecast?.backtest_points} años</strong>
                </div>
                <div>
                  <span>Serie usada</span>
                  <strong>
                    {forecast?.training_start_year}–{forecast?.training_end_year}
                  </strong>
                </div>
              </div>

              {forecast?.uses_provisional_data && (
                <p className="forecast-note">
                  La serie incluye 2025 provisional. El rango mostrado es una
                  aproximación basada en errores de backtesting, no una garantía.
                </p>
              )}
            </aside>
          </div>
        </Panel>
      </section>

      <footer>
        <span>
          Fuente: Banco de Guatemala · Comercio General · ETL validado.
        </span>
        <span>
          {summary.latest_year_is_provisional
            ? `${summary.latest_year}: cifra provisional.`
            : ""}
        </span>
      </footer>
    </main>
  );
}

export default App;
