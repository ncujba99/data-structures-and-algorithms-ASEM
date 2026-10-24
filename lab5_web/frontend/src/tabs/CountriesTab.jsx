import { useState } from "react";
import { api } from "../api.js";

export default function CountriesTab({ countries, changed, run, notify }) {
  const [editing, setEditing] = useState(null);   // code of the country being renamed

  const addCountry = (country) => run(async () => {
    await api.addCountry(country);
    changed();
    notify(`Страна «${country.name}» добавлена.`);
  });

  const renameCountry = (code, name) => run(async () => {
    await api.renameCountry(code, name);
    setEditing(null);
    changed();
    notify("Сохранено. Города и поезда этой страны показывают новое название.");
  });

  const deleteCountry = (country) => run(async () => {
    await api.deleteCountry(country.code);
    changed();
    notify(`Страна «${country.name}» удалена.`);
  });

  return (
    <>
      <section className="card">
        <h2>Справочник стран</h2>
        <p className="note">
          Связи: страна ← города (<code>cities.country_code</code>) ← поезда (<code>trains.destination_id</code>)
          и остановки (<code>train_stops.city_id</code>). Ключ страны — код ISO 3166 (<code>MD</code>,{" "}
          <code>RO</code>…): он короткий и никогда не меняется, поэтому годится как первичный ключ. Название можно
          менять свободно. Страну, в которой есть города, база удалить не даст.
        </p>
        <AddCountryForm onAdd={addCountry} />
      </section>
      <section className="card">
        <div className="scroll">
          <table>
            <thead><tr><th>Код</th><th>Название</th><th>Городов</th><th /></tr></thead>
            <tbody>
              {countries.map((country) =>
                country.code === editing ? (
                  <RenameRow key={country.code} country={country}
                             onSave={(name) => renameCountry(country.code, name)} onCancel={() => setEditing(null)} />
                ) : (
                  <tr key={country.code}>
                    <td><code>{country.code}</code></td>
                    <td>{country.name}</td>
                    <td>{country.cities}</td>
                    <td className="actions">
                      <button className="secondary" onClick={() => setEditing(country.code)}>Переименовать</button>
                      <button className="danger" onClick={() => deleteCountry(country)}>Удалить</button>
                    </td>
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}

function AddCountryForm({ onAdd }) {
  const submit = (event) => {
    event.preventDefault();
    const form = event.target;
    onAdd({ code: form.code.value.toUpperCase(), name: form.name.value })
      .then((ok) => ok && form.reset());
  };
  return (
    <form className="row" onSubmit={submit}>
      <label>Код <input name="code" size="4" maxLength="2" pattern="[A-Za-z]{2}" placeholder="PL" required /></label>
      <label>Название <input name="name" maxLength="100" required /></label>
      <button type="submit">Добавить страну</button>
    </form>
  );
}

function RenameRow({ country, onSave, onCancel }) {
  const [name, setName] = useState(country.name);
  return (
    <tr>
      <td><code>{country.code}</code></td>
      <td><input value={name} onChange={(e) => setName(e.target.value)} maxLength="100" /></td>
      <td>{country.cities}</td>
      <td className="actions">
        <button onClick={() => onSave(name)}>Сохранить</button>
        <button className="secondary" onClick={onCancel}>Отмена</button>
      </td>
    </tr>
  );
}
