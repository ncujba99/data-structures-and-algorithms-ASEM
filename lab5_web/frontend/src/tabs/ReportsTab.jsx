import { useEffect, useState } from "react";
import { api } from "../api.js";
import SqlBlock from "../components/SqlBlock.jsx";

export default function ReportsTab({ version, run }) {
  const [byCountry, setByCountry] = useState(null);
  const [busiest, setBusiest] = useState(null);

  useEffect(() => {
    run(async () => {
      const [countries, cities] = await Promise.all([api.reportByCountry(), api.reportBusiestCities()]);
      setByCountry(countries);
      setBusiest(cities);
    });
  }, [run, version]);

  return (
    <>
      <p className="note intro">
        Каждый отчёт — один запрос по нескольким таблицам. В коде он собирается на Python (SQLAlchemy),
        в базу уходит SQL. В лабораторной для каждого такого вопроса пришлось бы писать новый обход дерева.
      </p>
      {byCountry && (
        <Report title="Поезда по странам назначения" report={byCountry} columns={[
          ["country", "Страна"], ["cities", "Городов"], ["trains", "Поездов"],
          ["first_departure", "Первый"], ["last_departure", "Последний"],
        ]} />
      )}
      {busiest && (
        <Report title="Самые загруженные города" report={busiest} columns={[
          ["city", "Город"], ["country", "Страна"], ["trains_to", "Конечная"],
          ["trains_via", "Проходят"], ["total", "Всего"],
        ]} />
      )}
    </>
  );
}

function Report({ title, report, columns }) {
  const show = (value) => (value === null ? "—" : typeof value === "string" && /^\d\d:\d\d:\d\d$/.test(value) ? value.slice(0, 5) : value);
  return (
    <section className="card">
      <h2>{title}</h2>
      <div className="scroll">
        <table>
          <thead><tr>{columns.map(([key, label]) => <th key={key}>{label}</th>)}</tr></thead>
          <tbody>
            {report.rows.map((row, i) => (
              <tr key={i}>{columns.map(([key]) => <td key={key}>{show(row[key])}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
      <SqlBlock query={report} />
    </section>
  );
}
