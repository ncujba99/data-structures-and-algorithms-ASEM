import { useState } from "react";
import { api } from "../api.js";

export default function CitiesTab({ cities, countries, changed, run, notify }) {
  const [editing, setEditing] = useState(null);   // id of the city being edited

  const addCity = (city) => run(async () => {
    await api.addCity(city);
    changed();
    notify(`Город «${city.name}» добавлен.`);
  });

  const saveCity = (id, changes) => run(async () => {
    await api.updateCity(id, changes);
    setEditing(null);
    changed();
    notify("Сохранено. Все поезда показывают новое название: оно хранится в одной строке.");
  });

  const deleteCity = (city) => run(async () => {
    await api.deleteCity(city.id);
    changed();
    notify(`Город «${city.name}» удалён.`);
  });

  return (
    <>
      <section className="card">
        <h2>Справочник городов</h2>
        <p className="note">
          Каждый город хранится один раз, поезда ссылаются на него по <code>id</code>. Переименуйте город, и все
          маршруты изменятся сразу. Город, через который или до которого идут поезда, база удалить не даст
          (внешний ключ).
        </p>
        <AddCityForm countries={countries} onAdd={addCity} />
      </section>
      <section className="card">
        <div className="scroll">
          <table>
            <thead>
              <tr><th>Город</th><th>Страна</th><th>Конечная для</th><th>Проходят через</th><th /></tr>
            </thead>
            <tbody>
              {cities.map((city) =>
                city.id === editing ? (
                  <EditCityRow key={city.id} city={city} countries={countries}
                               onSave={(changes) => saveCity(city.id, changes)} onCancel={() => setEditing(null)} />
                ) : (
                  <tr key={city.id}>
                    <td>{city.name}</td>
                    <td>{city.country ?? "—"}</td>
                    <td>{city.trains_to}</td>
                    <td>{city.trains_via}</td>
                    <td className="actions">
                      <button className="secondary" onClick={() => setEditing(city.id)}>Изменить</button>
                      <button className="danger" onClick={() => deleteCity(city)}>Удалить</button>
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

function CountrySelect({ countries, value, onChange, name }) {
  return (
    <select name={name} value={value} onChange={onChange}>
      <option value="">неизвестна</option>
      {countries.map((c) => <option key={c.code} value={c.code}>{c.name}</option>)}
    </select>
  );
}

function AddCityForm({ countries, onAdd }) {
  const [country, setCountry] = useState("");
  const submit = (event) => {
    event.preventDefault();
    const form = event.target;
    onAdd({ name: form.name.value, country_code: country || null }).then((ok) => {
      if (!ok) return;
      form.reset();
      setCountry("");
    });
  };
  return (
    <form className="row" onSubmit={submit}>
      <label>Название <input name="name" maxLength="100" required /></label>
      <label>Страна <CountrySelect countries={countries} value={country} onChange={(e) => setCountry(e.target.value)} /></label>
      <button type="submit">Добавить город</button>
    </form>
  );
}

function EditCityRow({ city, countries, onSave, onCancel }) {
  const [name, setName] = useState(city.name);
  const [country, setCountry] = useState(city.country_code ?? "");
  return (
    <tr>
      <td><input value={name} onChange={(e) => setName(e.target.value)} maxLength="100" /></td>
      <td><CountrySelect countries={countries} value={country} onChange={(e) => setCountry(e.target.value)} /></td>
      <td>{city.trains_to}</td>
      <td>{city.trains_via}</td>
      <td className="actions">
        <button onClick={() => onSave({ name, country_code: country || null })}>Сохранить</button>
        <button className="secondary" onClick={onCancel}>Отмена</button>
      </td>
    </tr>
  );
}
