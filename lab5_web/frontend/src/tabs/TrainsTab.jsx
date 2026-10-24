import { useEffect, useState } from "react";
import { api, trainToInput } from "../api.js";

const NO_SEARCH = { number: "", city_id: "", match: "both", time_from: "", time_to: "" };

// How a train is linked to the searched city.
const MATCHES = [
  { id: "to", title: "до города" },
  { id: "via", title: "через город" },
  { id: "both", title: "оба" },
];

export default function TrainsTab({ cities, version, changed, run, notify }) {
  const [search, setSearch] = useState(NO_SEARCH);
  const [trains, setTrains] = useState({ items: [], total: 0 });
  const [adding, setAdding] = useState(false);
  // The number is typed digit by digit, so it is looked up only after a pause.
  const number = useDebounced(search.number, 300);

  useEffect(() => {
    let current = true;
    const show = (result) => current && setTrains(result);
    run(async () => {
      if (number === "") {
        const { number: _, match, ...filters } = search;
        show(await api.listTrains(search.city_id ? { ...filters, match } : filters));
        return;
      }
      // A missing number is an answer, not an error: it is shown in the table, not in a toast.
      try {
        show({ items: [await api.getTrain(Number(number))], total: 1 });
      } catch {
        show({ items: [], total: 0 });
      }
    });
    return () => { current = false; };
    // The number triggers a lookup through its debounced copy only.
  }, [run, number, search.city_id, search.match, search.time_from, search.time_to, version]);

  const addTrain = (train) => run(async () => {
    await api.addTrain(train);
    changed();
    setAdding(false);
    notify(`Поезд № ${train.number} добавлен.`);
  });

  const deleteTrain = (trainNumber) => run(async () => {
    const deleted = await api.deleteTrain(trainNumber);
    changed();
    // Undo puts back the deleted record itself, so changes made in between are kept.
    notify(`Поезд № ${trainNumber} удалён вместе с остановками.`, {
      actionText: "Отменить",
      onAction: () => run(async () => {
        await api.addTrain(trainToInput(deleted));
        changed();
        notify(`Поезд № ${trainNumber} восстановлен.`);
      }),
    });
  });

  return (
    <>
      <Search cities={cities} search={search} onChange={setSearch} />
      {adding
        ? <AddTrainForm cities={cities} onAdd={addTrain} onCancel={() => setAdding(false)} />
        : <button className="add-train" onClick={() => setAdding(true)}>+ Добавить поезд</button>}
      <TrainTable
        title={describe(search, cities)}
        trains={trains}
        city={number === "" && search.city_id ? Number(search.city_id) : null}
        onDelete={deleteTrain}
      />
    </>
  );
}

function useDebounced(value, delay) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    // Clearing the field shows the list at once.
    if (value === "") { setDebounced(value); return; }
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

// The table title says in words what is searched for.
function describe({ number, city_id, match, time_from, time_to }, cities) {
  if (number !== "") return `Поезд № ${number}`;
  const parts = [];
  const city = cities.find((c) => c.id === Number(city_id));
  if (city) parts.push({
    to: `до станции ${city.name}`,
    via: `проходящие через ${city.name}`,
    both: `до станции ${city.name} и через неё`,
  }[match]);
  if (time_from && time_to) parts.push(`отправление ${time_from}–${time_to}`);
  else if (time_from) parts.push(`отправление с ${time_from}`);
  else if (time_to) parts.push(`отправление до ${time_to}`);
  return parts.length ? `Поезда ${parts.join(", ")}` : "Все поезда (по возрастанию номера)";
}

function CitySelect({ cities, value, onChange, empty, required, exclude = [] }) {
  return (
    <select value={value} onChange={onChange} required={required}>
      <option value="">{empty}</option>
      {cities.filter((c) => !exclude.includes(c.id)).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
    </select>
  );
}

function Search({ cities, search, onChange }) {
  const set = (key) => (e) => onChange({ ...search, [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value });
  const byNumber = search.number !== "";
  const filtered = search.city_id || search.time_from || search.time_to;
  const emptyRange = search.time_from && search.time_to && search.time_from > search.time_to;

  return (
    <section className="card">
      <h2>Поиск</h2>
      <div className="search">
        <label>
          Номер поезда
          <input type="number" min="1" max="9999" placeholder="например, 50" value={search.number} onChange={set("number")} />
        </label>
        <span className="or">или</span>
        <fieldset className="filters" disabled={byNumber}>
          <label>
            Город
            <CitySelect cities={cities} value={search.city_id} empty="любой" onChange={set("city_id")} />
          </label>
          <div className="segmented" role="radiogroup" aria-label="Как поезд связан с городом"
               title={search.city_id ? "" : "Сначала выберите город"}>
            {MATCHES.map((m) => (
              <label key={m.id} className={search.match === m.id ? "on" : ""}>
                <input type="radio" name="match" value={m.id} checked={search.match === m.id}
                       disabled={!search.city_id} onChange={set("match")} />
                {m.title}
              </label>
            ))}
          </div>
          <label>Отправление с <input type="time" value={search.time_from} onChange={set("time_from")} /></label>
          <label>по <input type="time" value={search.time_to} onChange={set("time_to")} /></label>
        </fieldset>
        {(byNumber || filtered) && (
          <button type="button" className="secondary" onClick={() => onChange(NO_SEARCH)}>Сбросить</button>
        )}
      </div>
      {byNumber && <p className="hint">Поиск по номеру: фильтры не применяются.</p>}
      {!byNumber && emptyRange && <p className="hint warn">Время «с» позже времени «по»: таких поездов нет.</p>}
    </section>
  );
}

function AddTrainForm({ cities, onAdd, onCancel }) {
  const [destination, setDestination] = useState("");
  const [stops, setStops] = useState([]);   // city ids in route order

  const cityName = (id) => cities.find((c) => c.id === id)?.name ?? "?";
  const destinationId = destination ? Number(destination) : null;

  const move = (i, step) => {
    const next = [...stops];
    [next[i], next[i + step]] = [next[i + step], next[i]];
    setStops(next);
  };

  const submit = (event) => {
    event.preventDefault();
    const form = event.target;
    onAdd({
      number: Number(form.number.value),
      destination_id: destinationId,
      departure: form.departure.value,
      stops,
    });
  };

  return (
    <section className="card">
      <h2>Новый поезд</h2>
      <form onSubmit={submit}>
        <div className="row">
          <label>Номер <input name="number" type="number" min="1" max="9999" required autoFocus /></label>
          <label>Отправление <input name="departure" type="time" required /></label>
          <label>
            Конечная станция
            <CitySelect cities={cities} value={destination} empty="— выберите —" required exclude={stops}
                        onChange={(e) => setDestination(e.target.value)} />
          </label>
        </div>

        <h3 className="subhead">Маршрут</h3>
        <ol className="builder">
          <li className="terminal muted">Отправление с вокзала</li>
          {stops.map((id, i) => (
            <li key={id}>
              <span>{cityName(id)}</span>
              <span className="tools">
                <button type="button" className="icon" aria-label="Выше" disabled={i === 0} onClick={() => move(i, -1)}>↑</button>
                <button type="button" className="icon" aria-label="Ниже" disabled={i === stops.length - 1} onClick={() => move(i, 1)}>↓</button>
                <button type="button" className="icon" aria-label="Убрать" onClick={() => setStops(stops.filter((_, j) => j !== i))}>×</button>
              </span>
            </li>
          ))}
          <li className="add-stop">
            {/* Picking a city adds it at once; cities already on the route are not offered. */}
            <CitySelect cities={cities} value="" empty="+ промежуточная станция"
                        exclude={destinationId ? [...stops, destinationId] : stops}
                        onChange={(e) => e.target.value && setStops([...stops, Number(e.target.value)])} />
          </li>
          <li className="terminal">
            <strong>{destinationId ? cityName(destinationId) : "конечная станция не выбрана"}</strong>
          </li>
        </ol>

        <div className="row">
          <button type="submit">Добавить поезд</button>
          <button type="button" className="secondary" onClick={onCancel}>Отмена</button>
        </div>
      </form>
    </section>
  );
}

function Route({ stops, destination, highlight }) {
  const mark = (id) => (id === highlight ? "hit" : undefined);
  return (
    <ol className="route-line">
      {stops.map((s) => <li key={s.id} className={mark(s.id)}><span>{s.name}</span></li>)}
      <li className={["end", mark(destination.id)].filter(Boolean).join(" ")}><span>{destination.name}</span></li>
    </ol>
  );
}

// Whether the searched city ends the route or is passed on the way, and at which stop.
function Relation({ train, city }) {
  if (train.destination.id === city) return <span className="badge end">конечная</span>;
  const stop = train.stops.findIndex((s) => s.id === city) + 1;
  return (
    <span className="badge via" title={`${stop}-я остановка из ${train.stops.length}`}>
      проходящий · {stop}-я ост.
    </span>
  );
}

function TrainTable({ title, trains: { items, total }, city, onDelete }) {
  const note =
    total === 0 ? null :
    total > items.length ? `Показаны первые ${items.length} из ${total}.` : `Найдено: ${total}.`;
  return (
    <section className="card">
      <h2>{title}</h2>
      {total === 0 ? (
        <p className="empty">Ничего не найдено.</p>
      ) : (
        <div className="scroll">
          <table className="trains">
            <thead>
              <tr><th>№</th><th>Отпр.</th><th>Маршрут</th>{city && <th>Город</th>}<th>Страна</th><th /></tr>
            </thead>
            <tbody>
              {items.map((train) => (
                <tr key={train.number}>
                  <td className="num">{train.number}</td>
                  <td className="num">{train.departure.slice(0, 5)}</td>
                  <td><Route stops={train.stops} destination={train.destination} highlight={city} /></td>
                  {city && <td><Relation train={train} city={city} /></td>}
                  <td>{train.destination.country ?? "—"}</td>
                  <td><button className="danger" onClick={() => onDelete(train.number)}>Удалить</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {note && <p className="note">{note}</p>}
    </section>
  );
}
