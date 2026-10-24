import { useEffect, useState } from "react";
import { api } from "../api.js";

// Our station is not a city in the database: every train starts here.
const STATION = "Кишинёв";

// Departure windows; both ends are included by the API.
const WINDOWS = [
  { id: "any", title: "Любое", from: "", to: "" },
  { id: "night", title: "Ночь", hint: "00–06", from: "00:00", to: "05:59" },
  { id: "morning", title: "Утро", hint: "06–12", from: "06:00", to: "11:59" },
  { id: "day", title: "День", hint: "12–18", from: "12:00", to: "17:59" },
  { id: "evening", title: "Вечер", hint: "18–24", from: "18:00", to: "23:59" },
];

export default function SearchTab({ cities, version, run }) {
  const [form, setForm] = useState({ from: "", to: "", date: today(), window: "any" });
  const [query, setQuery] = useState(null);       // the search behind the results shown
  const [results, setResults] = useState(null);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });
  const cityName = (id) => cities.find((c) => c.id === Number(id))?.name ?? STATION;

  useEffect(() => {
    if (!query) return;
    let current = true;
    run(async () => {
      const { items } = await api.searchTrains(apiParams(query));
      if (current) setResults(items);
    });
    return () => { current = false; };
  }, [run, query, version]);

  const submit = (event) => {
    event.preventDefault();
    setQuery({ ...form });
  };

  // Our station is not a destination, so it can only stay on the "from" side.
  const swap = () => setForm({ ...form, from: form.to, to: form.from });

  return (
    <>
      <section className="card trip-card">
        <h2>Поиск поездов</h2>
        <form onSubmit={submit}>
          <div className="trip">
            <label className="grow">
              Откуда
              <select value={form.from} onChange={set("from")}>
                <option value="">{STATION}, наш вокзал</option>
                {cities.filter((c) => c.id !== Number(form.to)).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </label>
            <button type="button" className="swap" aria-label="Поменять местами" title="Поменять местами"
                    disabled={!form.from || !form.to} onClick={swap}>⇄</button>
            <label className="grow">
              Куда
              <select value={form.to} onChange={set("to")} required>
                <option value="">Выберите город</option>
                {cities.filter((c) => c.id !== Number(form.from)).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </label>
            <label>
              Дата
              <input type="date" value={form.date} min={today()} onChange={set("date")} required />
            </label>
          </div>

          <div className="when" role="radiogroup" aria-label="Время отправления">
            <span className="when-label">Отправление</span>
            {WINDOWS.map((w) => (
              <label key={w.id} className={form.window === w.id ? "pill on" : "pill"}>
                <input type="radio" name="window" value={w.id} checked={form.window === w.id} onChange={set("window")} />
                {w.title}{w.hint && <span className="pill-hint">{w.hint}</span>}
              </label>
            ))}
          </div>

          <button type="submit" className="find">Найти поезда</button>
        </form>
      </section>

      {query && results && (
        <section className="card">
          <div className="results-head">
            <h2>{cityName(query.from)} → {cityName(query.to)}</h2>
            <span className="muted">{formatDate(query.date)} · {plural(results.length)}</span>
          </div>
          {query.date === today() && <p className="hint">Сегодня: показаны поезда, которые ещё не ушли.</p>}
          {results.length === 0 ? (
            <p className="empty">
              Поездов нет. Попробуйте другое время отправления
              {query.from ? " или отправление с нашего вокзала" : ""}.
            </p>
          ) : (
            <ul className="results">
              {results.map((train) => (
                <Result key={train.number} train={train} from={Number(query.from) || null} to={Number(query.to)} />
              ))}
            </ul>
          )}
          <p className="note">Поезда ходят ежедневно. Время указано по отправлению с вокзала {STATION}.</p>
        </section>
      )}
    </>
  );
}

function Result({ train, from, to }) {
  // The whole route, from our station to the destination; the passenger rides from `from` to `to`.
  const route = [{ id: null, name: STATION }, ...train.stops, train.destination];
  const start = route.findIndex((c) => c.id === from);
  const end = route.findIndex((c) => c.id === to);
  const stopsOnTheWay = end - start - 1;

  return (
    <li className="result">
      <div className="result-time">
        <strong>{train.departure.slice(0, 5)}</strong>
        <span className="muted small">отправление</span>
      </div>
      <div className="result-body">
        <div className="result-title">
          Поезд № {train.number} <span className="muted">· до станции {train.destination.name}</span>
        </div>
        <ol className="route-line">
          {route.map((c, i) => (
            <li key={c.id ?? "station"}
                className={[i >= start && i <= end ? "ride" : "", i === start || i === end ? "edge" : ""].join(" ").trim() || undefined}>
              <span>{c.name}</span>
            </li>
          ))}
        </ol>
      </div>
      <div className="result-meta muted small">
        {stopsOnTheWay === 0 ? "без остановок" : `${stopsOnTheWay} ост. в пути`}
      </div>
    </li>
  );
}

// The form -> API query. On today's date, trains that have already left are not shown.
function apiParams({ from, to, date, window }) {
  const w = WINDOWS.find((x) => x.id === window);
  let timeFrom = w.from;
  if (date === today()) {
    const now = new Date().toTimeString().slice(0, 5);
    if (now > timeFrom) timeFrom = now;
  }
  return { from_id: from, to_id: to, time_from: timeFrom, time_to: w.to };
}

function today() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function formatDate(iso) {
  return new Date(`${iso}T00:00`).toLocaleDateString("ru-RU", { weekday: "short", day: "numeric", month: "long" });
}

function plural(n) {
  const forms = n % 10 === 1 && n % 100 !== 11 ? "поезд"
    : [2, 3, 4].includes(n % 10) && ![12, 13, 14].includes(n % 100) ? "поезда" : "поездов";
  return `${n} ${forms}`;
}
