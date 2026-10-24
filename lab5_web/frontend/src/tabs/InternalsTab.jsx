import { useEffect, useState } from "react";
import { api } from "../api.js";
import SqlBlock from "../components/SqlBlock.jsx";

export default function InternalsTab({ version, changed, run, notify }) {
  const [indexes, setIndexes] = useState([]);
  const [plans, setPlans] = useState(null);

  useEffect(() => {
    run(async () => {
      const [indexList, explained] = await Promise.all([api.listIndexes(), api.explain()]);
      setIndexes(indexList);
      setPlans(explained);
    });
  }, [run, version]);

  const bulkFill = () => run(async () => {
    const { added } = await api.bulkFill();
    changed();
    notify(`Добавлено поездов: ${added}.`);
  });

  const resetDemo = () => run(async () => {
    await api.resetDemo();
    changed();
    notify("Демо-данные восстановлены.");
  });

  return (
    <>
      <section className="card">
        <h2>Внутри это всё те же деревья</h2>
        <p className="note">
          Таблицы, связи и JOIN — это модель для нас. Хранит и ищет данные PostgreSQL в B+-деревьях: по одному
          на каждый первичный ключ, UNIQUE и индекс. Это дерево поиска из лабораторной, только в узле сотни ключей,
          а не один, и оно само остаётся сбалансированным.
        </p>
        <p className="note">
          В коде запросы пишутся на Python: модели SQLAlchemy описывают таблицы, а <code>select()</code>,{" "}
          <code>where()</code>, <code>join()</code> собирают запрос. SQLAlchemy переводит его в SQL, PostgreSQL
          выбирает план. Ниже для каждого поиска видны все три шага.
        </p>
        <p className="note">
          На 9 строках базе проще прочитать таблицу целиком. Заполните её до 9 999 поездов, и планы перейдут на
          индексы, а высота деревьев станет 2.
        </p>
        <div className="row">
          <button onClick={bulkFill}>Заполнить номера 1…9999</button>
          <button className="secondary" onClick={resetDemo}>Вернуть демо-данные</button>
        </div>
      </section>

      <section className="card">
        <h2>B+-деревья в базе</h2>
        <div className="scroll">
          <table>
            <thead><tr><th>Таблица</th><th>Индекс</th><th>Высота</th><th>Размер</th><th>Определение</th></tr></thead>
            <tbody>
              {indexes.map((ix) => (
                <tr key={ix.index_name}>
                  <td>{ix.table_name}</td>
                  <td><code>{ix.index_name}</code></td>
                  <td>{ix.height}</td>
                  <td>{ix.size}</td>
                  <td className="muted small">{ix.definition.replace(/ USING btree/, "").replace(/^CREATE (UNIQUE )?INDEX \S+ ON public\./, "")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {plans && (
        <section className="card">
          <h2>Как база выполняет поиск (EXPLAIN), строк в trains: {plans.rows}</h2>
          {plans.queries.map((q) => (
            <div key={q.title} className="plan">
              <h3>{q.title}</h3>
              <div className="steps">
                <div>
                  <p className="query-label">1. Python (SQLAlchemy)</p>
                  <pre>{q.python.trim()}</pre>
                </div>
                <div>
                  <p className="query-label">2. SQL</p>
                  <pre>{q.sql.trim()}</pre>
                </div>
              </div>
              <p className="query-label">3. План PostgreSQL (EXPLAIN)</p>
              <pre className="plan-text">{q.plan.join("\n")}</pre>
            </div>
          ))}
        </section>
      )}
    </>
  );
}
