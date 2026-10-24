import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import Toast from "./components/Toast.jsx";
import SearchTab from "./tabs/SearchTab.jsx";
import TrainsTab from "./tabs/TrainsTab.jsx";
import CitiesTab from "./tabs/CitiesTab.jsx";
import CountriesTab from "./tabs/CountriesTab.jsx";
import ReportsTab from "./tabs/ReportsTab.jsx";
import InternalsTab from "./tabs/InternalsTab.jsx";

const TABS = [
  { id: "search", title: "Поиск поездов", Component: SearchTab },
  { id: "trains", title: "Расписание", Component: TrainsTab },
  { id: "cities", title: "Города", Component: CitiesTab },
  { id: "countries", title: "Страны", Component: CountriesTab },
  { id: "reports", title: "Отчёты", Component: ReportsTab },
  { id: "internals", title: "Под капотом", Component: InternalsTab },
];

export default function App() {
  const [tab, setTab] = useState("search");
  const [toast, setToast] = useState(null);
  // Cities and countries are shared: the train forms pick from them, the cities tab edits them.
  const [cities, setCities] = useState([]);
  const [countries, setCountries] = useState([]);
  // Bumped after any change to the data, so every tab reloads what it shows.
  const [version, setVersion] = useState(0);

  const notify = useCallback((message, extra = {}) => setToast({ message, ...extra, id: Date.now() }), []);

  // Runs an action and shows any error in the toast instead of the console.
  // Resolves to true when the action succeeded.
  const run = useCallback(
    (action) => action().then(() => true, (e) => {
      notify(e.message, { error: true });
      return false;
    }),
    [notify],
  );

  const changed = useCallback(() => setVersion((v) => v + 1), []);

  useEffect(() => {
    run(async () => {
      const [cityList, countryList] = await Promise.all([api.listCities(), api.listCountries()]);
      setCities(cityList);
      setCountries(countryList);
    });
  }, [run, version]);

  const { Component } = TABS.find((t) => t.id === tab);

  return (
    <>
      <header>
        <h1>Справочная вокзала</h1>
        <p>ЛР №5, Задание 1, сделанное «по-взрослому»: React → FastAPI → PostgreSQL.</p>
        <nav>
          {TABS.map((t) => (
            <button key={t.id} className={t.id === tab ? "tab active" : "tab"} onClick={() => setTab(t.id)}>
              {t.title}
            </button>
          ))}
        </nav>
      </header>
      <main>
        <Component
          cities={cities}
          countries={countries}
          version={version}
          changed={changed}
          run={run}
          notify={notify}
        />
      </main>
      {toast && <Toast key={toast.id} {...toast} onClose={() => setToast(null)} />}
    </>
  );
}
