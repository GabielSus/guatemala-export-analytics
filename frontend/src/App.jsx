import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  BarChart3,
  Boxes,
  Database,
  RefreshCw,
  TrendingUp,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { analyticsApi } from "./api";
import { formatNumber, formatPct, formatUsd, formatUsdFull } from "./format";

const chartColors = ["#22c55e", "#38bdf8", "#a78bfa", "#f59e0b", "#fb7185", "#2dd4bf"];

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
  const [loading, setLoading] = useState(true);
  const [sectionLoading, setSectionLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadBase() {
    setLoading(true);
    setError("");
    try {
      const [summaryData, yearlyData, growthData, yearsData] = await Promise.all([
        analyticsApi.summary(),
        analyticsApi.yearly(),
        analyticsApi.growth(),
        analyticsApi.years(),
      ]);
      setSummary(summaryData);
      setYearly(yearlyData);
      setGrowth(growthData);
      setYears(yearsData.years);
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
      .catch((err) => active && setError(err.message))
      .finally(() => active && setSectionLoading(false));
    return () => { active = false; };
  }, [selectedYear]);

  const selectedGrowth = useMemo(
    () => growth.find((item) => item.year === selectedYear),
    [growth, selectedYear],
  );

  if (loading) {
    return <main className="center-state"><RefreshCw className="spin" /> Cargando dashboard...</main>;
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
          <div className="eyebrow"><Activity size={15} /> PORTFOLIO DATA PROJECT</div>
          <h1>Guatemala Export Analytics</h1>
          <p>Comercio General · Exportaciones por inciso arancelario · 2002–2025</p>
        </div>
        <div className="header-controls">
          <label>
            Año analizado
            <select value={selectedYear ?? ""} onChange={(e) => setSelectedYear(Number(e.target.value))}>
              {years.map((year) => <option value={year} key={year}>{year}</option>)}
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
          detail={selectedGrowth?.is_provisional ? "Cifra provisional" : "Cifra oficial del dataset"}
        />
        <KpiCard
          icon={BarChart3}
          label="Crecimiento interanual"
          value={formatPct(selectedGrowth?.growth_pct)}
          detail={selectedGrowth?.previous_year_total_usd ? `vs. ${selectedYear - 1}` : "Sin año previo disponible"}
          positive={selectedGrowth?.growth_pct == null || selectedGrowth.growth_pct >= 0}
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
        <Panel title="Evolución histórica" subtitle="Valor total anual de exportaciones en USD">
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={yearly} margin={{ top: 10, right: 15, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#253044" />
                <XAxis dataKey="year" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tickFormatter={formatUsd} tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} width={74} />
                <Tooltip formatter={(value) => formatUsdFull(value)} labelFormatter={(value) => `Año ${value}`} contentStyle={{ background: "#111827", border: "1px solid #334155", borderRadius: 10 }} />
                <Line type="monotone" dataKey="total_usd" stroke="#22c55e" strokeWidth={3} dot={false} activeDot={{ r: 5 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Panel>

        <Panel title="Variación anual" subtitle="Crecimiento porcentual respecto al año anterior">
          <div className="chart-area">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={growth.filter((g) => g.growth_pct !== null)}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#253044" />
                <XAxis dataKey="year" tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tickFormatter={(value) => `${value}%`} tick={{ fill: "#94a3b8", fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip formatter={(value) => `${Number(value).toFixed(2)}%`} contentStyle={{ background: "#111827", border: "1px solid #334155", borderRadius: 10 }} />
                <Bar dataKey="growth_pct" radius={[4, 4, 0, 0]} fill="#38bdf8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Panel>
      </section>

      <section className="dashboard-grid">
        <Panel title={`Top incisos · ${selectedYear}`} subtitle="Mayores valores exportados por código arancelario">
          {sectionLoading ? <div className="panel-loading">Actualizando...</div> : (
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
                          <span title={item.description ?? ""}>
                            {item.description || "Descripción pendiente de catálogo SAC"}
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

        <Panel title={`Principales capítulos · ${selectedYear}`} subtitle="Participación de los 10 capítulos con mayor valor">
          <div className="chapter-layout">
            <div className="donut">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={chapters} dataKey="total_usd" nameKey="chapter" innerRadius={58} outerRadius={90} paddingAngle={2}>
                    {chapters.map((entry, index) => <Cell key={entry.chapter} fill={chartColors[index % chartColors.length]} />)}
                  </Pie>
                  <Tooltip
                    formatter={(value) => formatUsdFull(value)}
                    labelFormatter={(label) => `Capítulo ${label}`}
                    contentStyle={{ background: "#111827", border: "1px solid #334155", borderRadius: 10 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="chapter-list">
              {chapters.slice(0, 6).map((chapter, index) => (
                <div key={chapter.chapter} title={chapter.description ?? ""}>
                  <span>
                    <i style={{ background: chartColors[index % chartColors.length] }} />
                    <b>Cap. {chapter.chapter}</b>
                    <em>{chapter.description || "Sin descripción"}</em>
                  </span>
                  <strong>{chapter.share_pct.toFixed(2)}%</strong>
                </div>
              ))}
            </div>
          </div>
        </Panel>
      </section>

      <footer>
        <span>Fuente: Banco de Guatemala · Comercio General · ETL validado.</span>
        <span>{summary.latest_year_is_provisional ? `${summary.latest_year}: cifra provisional.` : ""}</span>
      </footer>
    </main>
  );
}

export default App;
