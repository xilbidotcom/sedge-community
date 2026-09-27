// Copyright 2026 Xilbi Sistemas de Informacion SL
// SPDX-License-Identifier: Apache-2.0
import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  Code2,
  Download,
  ExternalLink,
  FileJson,
  Home,
  Info,
  LayoutGrid,
  LoaderCircle,
  Play,
  RotateCcw,
  Search,
  Sun,
  Building2,
  X,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from "recharts";
import Markdown from "react-markdown";
import { fundingDisclaimer } from "./legal";
import {
  defaults,
  estimateRows,
  csvText,
  chartData,
  errorMessage,
} from "./data";
import "./styles.css";

const articles = Object.entries(
  import.meta.glob("../../docs/help/*.md", {
    query: "?raw",
    import: "default",
    eager: true,
  }),
).map(([path, text]) => ({
  id: path.split("/").pop().replace(".md", ""),
  title: text.match(/^# (.+)$/m)?.[1],
  text,
}));
const number = (value) =>
  new Intl.NumberFormat("en-GB", { maximumFractionDigits: 2 }).format(value);
const stamp = (value) =>
  new Intl.DateTimeFormat("en-GB", {
    timeZone: "UTC",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  }).format(new Date(value));
const series = [
  { key: "load_kw", label: "Demand", color: "#176a8c" },
  { key: "pv_kw", label: "Solar PV", color: "#b07b11" },
  { key: "grid_kw", label: "Grid exchange", color: "#2e8b70" },
];

function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function Field({ label, children, suffix }) {
  return (
    <label className="field">
      <span>
        {label}
        {suffix && <small>{suffix}</small>}
      </span>
      {children}
    </label>
  );
}

function App() {
  const [page, setPage] = useState("generate");
  const [scenarios, setScenarios] = useState([]);
  const [config, setConfig] = useState(defaults);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [online, setOnline] = useState(null);
  const [view, setView] = useState("chart");
  const [tablePage, setTablePage] = useState(0);
  const [visible, setVisible] = useState(["load_kw", "pv_kw", "grid_kw"]);
  const [query, setQuery] = useState("");
  const [article, setArticle] = useState("01-getting-started");
  const pending = useRef(null);
  const form = useRef(null);
  useEffect(() => {
    const controller = new AbortController();
    fetch("/api/v1/scenarios", { signal: controller.signal })
      .then((r) => {
        if (!r.ok) throw Error();
        return r.json();
      })
      .then((data) => {
        setScenarios(data);
        setOnline(true);
      })
      .catch((e) => {
        if (e.name !== "AbortError") setOnline(false);
      });
    return () => controller.abort();
  }, []);
  const points = useMemo(() => chartData(result?.rows || []), [result]);
  const selected = scenarios.find((s) => s.id === config.scenario_id);
  const rows = estimateRows(config);
  const dirty =
    result && JSON.stringify(config) !== JSON.stringify(result.configuration);
  function update(key, value) {
    setConfig((c) => ({ ...c, [key]: value }));
    setError("");
  }
  function choose(id) {
    const chosen = scenarios.find((s) => s.id === id);
    if (chosen) setConfig((c) => ({ ...c, ...chosen.defaults }));
    setPage("generate");
    setError("");
  }
  async function generate(event) {
    event.preventDefault();
    if (!form.current.reportValidity() || rows > 50000 || busy) return;
    const controller = new AbortController();
    pending.current = controller;
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/v1/generate", {
        method: "POST",
        signal: controller.signal,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(errorMessage(data));
      setResult(data);
      setTablePage(0);
      setView("chart");
      setOnline(true);
    } catch (e) {
      if (e.name !== "AbortError")
        setError(e.message || "The API could not be reached.");
    } finally {
      setBusy(false);
      pending.current = null;
    }
  }
  const help = () => {
    setPage("help");
    setArticle("01-getting-started");
  };
  return (
    <div className="app">
      <header className="topbar">
        <button
          className="brand"
          onClick={() => setPage("generate")}
          aria-label="SEDGE Community home"
        >
          <img src="/brand/sedge-logo.png" alt="SEDGE" />
          <span>
            Community <small>1.0.2</small>
          </span>
        </button>
        <nav aria-label="Main navigation">
          {[
            ["generate", Activity, "Generate"],
            ["scenarios", LayoutGrid, "Scenarios"],
            ["help", BookOpen, "Help"],
            ["about", Info, "About"],
          ].map(([id, Icon, label]) => (
            <button
              key={id}
              className={page === id ? "active" : ""}
              aria-current={page === id ? "page" : undefined}
              onClick={() => setPage(id)}
            >
              <Icon size={17} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <a
          className="company"
          href="https://www.xilbi.com/"
          aria-label="XILBI website"
          target="_blank"
          rel="noreferrer"
        >
          <img src="/brand/xilbi.png" alt="XILBI" />
        </a>
      </header>
      <main>
        {page === "generate" && (
          <>
            <div className="page-heading">
              <div>
                <p className="eyebrow">SYNTHETIC ENERGY DATA</p>
                <h1>Generate dataset</h1>
              </div>
              <div className="status">
                <span className={`dot ${online === false ? "offline" : ""}`} />
                {online === null
                  ? "Connecting"
                  : online
                    ? "API connected"
                    : "API unavailable"}
              </div>
            </div>
            <div className="workspace">
              <form ref={form} onSubmit={generate} className="configuration">
                <div className="section-heading">
                  <h2>Scenario</h2>
                  <button
                    className="icon"
                    type="button"
                    title="Reset settings"
                    aria-label="Reset settings"
                    disabled={busy}
                    onClick={() => {
                      setConfig(defaults);
                      setError("");
                    }}
                  >
                    <RotateCcw size={17} />
                  </button>
                </div>
                <fieldset disabled={busy}>
                  <Field label="Template">
                    <select
                      value={config.scenario_id}
                      onChange={(e) => choose(e.target.value)}
                    >
                      {scenarios.length ? (
                        scenarios.map((s) => (
                          <option key={s.id} value={s.id}>
                            {s.name}
                          </option>
                        ))
                      ) : (
                        <option value={config.scenario_id}>
                          Home with rooftop PV
                        </option>
                      )}
                    </select>
                  </Field>
                  <div className="field-row">
                    <Field label="Start date" suffix="UTC">
                      <input
                        required
                        type="date"
                        min="2000-01-01"
                        max="2100-12-01"
                        value={config.start_date}
                        onChange={(e) => update("start_date", e.target.value)}
                      />
                    </Field>
                    <Field label="Duration" suffix="days">
                      <input
                        required
                        type="number"
                        min="1"
                        max="31"
                        value={config.days}
                        onChange={(e) =>
                          update(
                            "days",
                            e.target.value === "" ? "" : Number(e.target.value),
                          )
                        }
                      />
                    </Field>
                  </div>
                  <div className="field-row">
                    <Field label="Interval">
                      <select
                        value={config.resolution_minutes}
                        onChange={(e) =>
                          update("resolution_minutes", Number(e.target.value))
                        }
                      >
                        {[5, 15, 30, 60].map((v) => (
                          <option key={v} value={v}>
                            {v} minutes
                          </option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Buildings">
                      <input
                        required
                        type="number"
                        min="1"
                        max="20"
                        value={config.buildings}
                        onChange={(e) =>
                          update(
                            "buildings",
                            e.target.value === "" ? "" : Number(e.target.value),
                          )
                        }
                      />
                    </Field>
                  </div>
                  <h2 className="subheading">Energy profile</h2>
                  <Field label="Daily demand per building" suffix="kWh">
                    <input
                      required
                      type="number"
                      min="1"
                      max="300"
                      step="0.1"
                      value={config.daily_load_kwh}
                      onChange={(e) =>
                        update(
                          "daily_load_kwh",
                          e.target.value === "" ? "" : Number(e.target.value),
                        )
                      }
                    />
                  </Field>
                  <Field label="PV capacity per building" suffix="kW">
                    <input
                      required
                      type="number"
                      min="0"
                      max="50"
                      step="0.1"
                      value={config.pv_capacity_kw}
                      onChange={(e) =>
                        update(
                          "pv_capacity_kw",
                          e.target.value === "" ? "" : Number(e.target.value),
                        )
                      }
                    />
                  </Field>
                  <Field
                    label="Variability"
                    suffix={`${Math.round(config.variability * 100)}%`}
                  >
                    <input
                      aria-label="Variability"
                      type="range"
                      min="0"
                      max="0.5"
                      step="0.01"
                      value={config.variability}
                      onChange={(e) =>
                        update("variability", Number(e.target.value))
                      }
                    />
                  </Field>
                  <Field label="Random seed">
                    <input
                      required
                      type="number"
                      min="0"
                      max="4294967295"
                      value={config.seed}
                      onChange={(e) =>
                        update(
                          "seed",
                          e.target.value === "" ? "" : Number(e.target.value),
                        )
                      }
                    />
                  </Field>
                </fieldset>
                <p className={rows > 50000 ? "limit error-text" : "limit"}>
                  {number(rows)} records <span>/ 50,000 maximum</span>
                </p>
                {error && (
                  <p role="alert" className="error-text">
                    {error}
                  </p>
                )}
                <div className="generate-actions">
                  <button
                    type="submit"
                    className="primary"
                    disabled={busy || rows > 50000}
                  >
                    {busy ? (
                      <LoaderCircle size={17} className="spin" />
                    ) : (
                      <Play size={17} />
                    )}{" "}
                    {busy ? "Generating" : "Generate dataset"}
                  </button>
                  {busy && (
                    <button
                      type="button"
                      className="icon"
                      title="Cancel generation"
                      onClick={() => pending.current?.abort()}
                    >
                      <X size={18} />
                    </button>
                  )}
                </div>
                <button type="button" className="text-button" onClick={help}>
                  <BookOpen size={15} /> Generation guide
                </button>
              </form>
              <section
                className="results"
                aria-label="Generated dataset"
                aria-busy={busy}
              >
                <div className="section-heading">
                  <div>
                    <h2>{result ? "Dataset preview" : "Preview"}</h2>
                    {result && (
                      <p className="muted dataset-name">{result.dataset_id}</p>
                    )}
                  </div>
                  {result && (
                    <div className="download-actions">
                      <button
                        title="Download complete CSV"
                        onClick={() =>
                          download(
                            `${result.dataset_id}.csv`,
                            csvText(result.rows),
                            "text/csv",
                          )
                        }
                      >
                        <Download size={16} /> CSV
                      </button>
                      <button
                        title="Download JSON with configuration and metadata"
                        onClick={() =>
                          download(
                            `${result.dataset_id}.json`,
                            JSON.stringify(result, null, 2),
                            "application/json",
                          )
                        }
                      >
                        <FileJson size={16} /> JSON
                      </button>
                    </div>
                  )}
                </div>
                {!result ? (
                  <div className="empty">
                    <Activity size={48} strokeWidth={1} />
                    <h3>No dataset generated</h3>
                    <p>
                      {selected?.name || "Home with rooftop PV"} ·{" "}
                      {number(rows)} records
                    </p>
                  </div>
                ) : (
                  <>
                    {dirty && (
                      <p className="pending-note">
                        Settings changed · Preview shows the last generated
                        dataset.
                      </p>
                    )}
                    <div className="metrics">
                      {[
                        ["Demand", result.summary.load_kwh, "kWh"],
                        ["Solar generation", result.summary.pv_kwh, "kWh"],
                        ["Grid import", result.summary.import_kwh, "kWh"],
                        ["Grid export", result.summary.export_kwh, "kWh"],
                      ].map(([label, value, unit]) => (
                        <div key={label}>
                          <span>{label}</span>
                          <strong>
                            {number(value)} <small>{unit}</small>
                          </strong>
                        </div>
                      ))}
                    </div>
                    <div
                      className="tabs"
                      role="tablist"
                      aria-label="Dataset views"
                    >
                      {["chart", "data", "metadata"].map((id) => (
                        <button
                          id={`tab-${id}`}
                          aria-controls={`panel-${id}`}
                          aria-selected={view === id}
                          role="tab"
                          key={id}
                          onClick={() => setView(id)}
                          className={view === id ? "active" : ""}
                        >
                          {id[0].toUpperCase() + id.slice(1)}
                        </button>
                      ))}
                    </div>
                    <div
                      role="tabpanel"
                      id={`panel-${view}`}
                      aria-labelledby={`tab-${view}`}
                    >
                      {view === "chart" && (
                        <>
                          <div className="chart-heading">
                            <h3>
                              Power over time <span>kW · UTC</span>
                            </h3>
                            <div className="legend">
                              {series.map((s) => (
                                <label
                                  key={s.key}
                                  style={{ "--series": s.color }}
                                >
                                  <input
                                    type="checkbox"
                                    checked={visible.includes(s.key)}
                                    onChange={() =>
                                      setVisible((v) =>
                                        v.includes(s.key)
                                          ? v.filter((k) => k !== s.key)
                                          : [...v, s.key],
                                      )
                                    }
                                  />
                                  {s.label}
                                </label>
                              ))}
                            </div>
                          </div>
                          <div className="chart">
                            <ResponsiveContainer width="100%" height="100%">
                              <LineChart
                                data={points}
                                margin={{
                                  top: 12,
                                  right: 12,
                                  bottom: 12,
                                  left: 0,
                                }}
                              >
                                <CartesianGrid
                                  stroke="#e5ebe9"
                                  vertical={false}
                                />
                                <XAxis
                                  dataKey="timestamp"
                                  tickFormatter={stamp}
                                  minTickGap={65}
                                  tick={{ fontSize: 11 }}
                                />
                                <YAxis width={45} tick={{ fontSize: 11 }} />
                                <Tooltip
                                  labelFormatter={stamp}
                                  formatter={(v, n) => [
                                    `${number(v)} kW`,
                                    series.find((s) => s.key === n)?.label || n,
                                  ]}
                                />
                                <ReferenceLine y={0} stroke="#b8c7c3" />
                                {series
                                  .filter((s) => visible.includes(s.key))
                                  .map((s) => (
                                    <Line
                                      key={s.key}
                                      type="linear"
                                      dataKey={s.key}
                                      stroke={s.color}
                                      strokeWidth={1.7}
                                      dot={false}
                                      isAnimationActive={false}
                                    />
                                  ))}
                              </LineChart>
                            </ResponsiveContainer>
                          </div>
                          <p className="muted chart-note">
                            {number(result.summary.rows)} records ·{" "}
                            {result.summary.buildings} building
                            {result.summary.buildings > 1 ? "s" : ""} ·{" "}
                            {result.configuration.resolution_minutes}-minute
                            intervals
                            {result.summary.buildings > 1
                              ? " · Summed building power"
                              : ""}
                            {result.rows.length / result.summary.buildings > 900
                              ? " · Chart sampled; downloads include every record"
                              : ""}
                          </p>
                        </>
                      )}
                      {view === "data" && (
                        <>
                          <div className="table-scroll">
                            <table>
                              <thead>
                                <tr>
                                  <th>Timestamp (UTC)</th>
                                  <th>Building</th>
                                  <th>Demand (kW)</th>
                                  <th>PV (kW)</th>
                                  <th>Grid (kW)</th>
                                  <th>Temp. (°C)</th>
                                </tr>
                              </thead>
                              <tbody>
                                {result.rows
                                  .slice(tablePage * 15, (tablePage + 1) * 15)
                                  .map((r) => (
                                    <tr key={`${r.timestamp}-${r.building_id}`}>
                                      <td>{stamp(r.timestamp)}</td>
                                      <td>{r.building_id}</td>
                                      <td>{number(r.load_kw)}</td>
                                      <td>{number(r.pv_kw)}</td>
                                      <td>{number(r.grid_kw)}</td>
                                      <td>{number(r.temperature_c)}</td>
                                    </tr>
                                  ))}
                              </tbody>
                            </table>
                          </div>
                          <div className="pagination">
                            <span>
                              {tablePage * 15 + 1}–
                              {Math.min(
                                (tablePage + 1) * 15,
                                result.rows.length,
                              )}{" "}
                              of {number(result.rows.length)}
                            </span>
                            <button
                              className="icon"
                              aria-label="Previous rows"
                              title="Previous rows"
                              disabled={!tablePage}
                              onClick={() => setTablePage((p) => p - 1)}
                            >
                              <ArrowLeft size={16} />
                            </button>
                            <button
                              className="icon"
                              aria-label="Next rows"
                              title="Next rows"
                              disabled={
                                (tablePage + 1) * 15 >= result.rows.length
                              }
                              onClick={() => setTablePage((p) => p + 1)}
                            >
                              <ArrowRight size={16} />
                            </button>
                          </div>
                        </>
                      )}
                      {view === "metadata" && (
                        <div className="metadata">
                          <dl>
                            <dt>Edition</dt>
                            <dd>
                              {result.edition} {result.version}
                            </dd>
                            <dt>Method</dt>
                            <dd>{result.methodology}</dd>
                            <dt>Random seed</dt>
                            <dd>{result.configuration.seed}</dd>
                            <dt>Time convention</dt>
                            <dd>UTC, end-exclusive</dd>
                            <dt>Storage</dt>
                            <dd>Browser memory only</dd>
                          </dl>
                          <h3>Limitations</h3>
                          <ul>
                            {result.warnings.map((w) => (
                              <li key={w}>{w}</li>
                            ))}
                          </ul>
                          <details>
                            <summary>Generation configuration</summary>
                            <pre>
                              {JSON.stringify(result.configuration, null, 2)}
                            </pre>
                          </details>
                        </div>
                      )}
                    </div>
                    <div className="result-footer">
                      <span>
                        <Check size={15} /> Generated
                      </span>
                      <span>Illustrative synthetic data</span>
                      <button
                        className="text-button"
                        onClick={() => {
                          setPage("help");
                          setArticle("02-methodology");
                        }}
                      >
                        Method and limitations <ArrowRight size={14} />
                      </button>
                    </div>
                  </>
                )}
              </section>
            </div>
          </>
        )}
        {page === "scenarios" && (
          <>
            <div className="page-heading">
              <div>
                <p className="eyebrow">STARTER SCENARIOS</p>
                <h1>Scenario library</h1>
              </div>
              <span className="muted">3 templates</span>
            </div>
            <div className="scenario-list">
              {scenarios.map((s, i) => {
                const Icon = [Home, Sun, Building2][i];
                return (
                  <article key={s.id}>
                    <Icon size={29} strokeWidth={1.4} />
                    <div>
                      <span className="eyebrow">{s.category}</span>
                      <h2>{s.name}</h2>
                      <p>{s.description}</p>
                      <dl>
                        <dt>Daily demand</dt>
                        <dd>{s.defaults.daily_load_kwh} kWh</dd>
                        <dt>PV capacity</dt>
                        <dd>{s.defaults.pv_capacity_kw} kW</dd>
                        <dt>Duration</dt>
                        <dd>7 days</dd>
                      </dl>
                    </div>
                    <button onClick={() => choose(s.id)}>
                      Use scenario <ArrowRight size={17} />
                    </button>
                  </article>
                );
              })}
              {!scenarios.length && (
                <p role="alert">
                  Scenarios are unavailable. Check that the Community API is
                  running.
                </p>
              )}
            </div>
          </>
        )}
        {page === "help" && (
          <>
            <div className="page-heading">
              <div>
                <p className="eyebrow">DOCUMENTATION</p>
                <h1>Help</h1>
              </div>
              <a
                className="button"
                href="/api/docs"
                target="_blank"
                rel="noreferrer"
              >
                <Code2 size={16} /> API reference <ExternalLink size={14} />
              </a>
            </div>
            <div className="help-layout">
              <aside>
                <label className="search">
                  <Search size={17} />
                  <input
                    aria-label="Search help"
                    placeholder="Search help"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </label>
                <nav aria-label="Help articles">
                  {articles
                    .filter((a) =>
                      a.text.toLowerCase().includes(query.toLowerCase()),
                    )
                    .map((a) => (
                      <button
                        key={a.id}
                        className={article === a.id ? "active" : ""}
                        onClick={() => setArticle(a.id)}
                      >
                        {a.title}
                        <ArrowRight size={14} />
                      </button>
                    ))}
                </nav>
                {!articles.some((a) =>
                  a.text.toLowerCase().includes(query.toLowerCase()),
                ) && <p>No matching articles.</p>}
              </aside>
              <article className="prose">
                <Markdown>
                  {articles.find((a) => a.id === article)?.text || ""}
                </Markdown>
              </article>
            </div>
          </>
        )}
        {page === "about" && (
          <>
            <div className="page-heading">
              <div>
                <p className="eyebrow">APACHE-2.0 · VERSION 1.0.2</p>
                <h1>SEDGE Community</h1>
              </div>
            </div>
            <article className="prose about">
              <h2>Synthetic Energy Data Generation Engine</h2>
              <p>
                A small, standalone open-source edition for learning,
                demonstrations and prototyping. It generates illustrative
                demand, solar production, grid exchange and temperature series
                from simple seeded profiles.
              </p>
              <h2>Scope</h2>
              <p>
                Generated results are held in memory and can be downloaded as
                CSV or JSON. Accounts, recipes, packages, ML, simulation engines
                and orchestration are not included.
              </p>
              <h2>Licensing and identity</h2>
              <p>
                Community source code and documentation are licensed under
                Apache-2.0. Copyright 2026 Xilbi Sistemas de Informacion SL.
                Logos and names retain their respective trademark terms; the
                source-code licence does not grant trademark rights.
              </p>
              <p>
                <a href="/legal/LICENSE" download>
                  Apache-2.0 licence
                </a>{" "}
                · <a href="/legal/NOTICE">Attribution notice</a> ·{" "}
                <a href="/legal/BRANDING.md">Branding terms</a> ·{" "}
                <a href="/legal/THIRD_PARTY_NOTICES.md">Third-party notices</a>{" "}
                ·{" "}
                <a href="/legal/THIRD_PARTY_LICENCES.txt">
                  Dependency licences
                </a>
              </p>
              <h2>Funding and acknowledgement</h2>
              <p>{fundingDisclaimer}</p>
              <p>
                Funding does not imply endorsement or certification.{" "}
                <a href="/legal/FUNDING.md">Funding statement</a>
              </p>
              <h2>Local by design</h2>
              <p>
                No authentication, database or background worker. Generated data
                stays in browser memory until downloaded. Do not expose this
                edition to the public Internet.
              </p>
            </article>
          </>
        )}
      </main>
      <footer>
        <div className="funding">
          <img src="/brand/eu-funding.png" alt="Funded by the European Union" />
          <p>
            {fundingDisclaimer} <a href="/legal/FUNDING.md">Funding details</a>
          </p>
        </div>
        <div className="footer-right">
          <img src="/brand/o-cei-logo.png" alt="O-CEI" />
          <span>
            SEDGE Community 1.0.2
            <br />
            <a href="/legal/LICENSE">Apache-2.0</a>
          </span>
        </div>
      </footer>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
