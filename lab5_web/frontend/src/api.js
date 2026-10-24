// Every API path ends with "/", as the backend defines them; without it FastAPI answers with a redirect.
async function request(method, path, body) {
  const response = await fetch(`/api${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new Error(errorText(data, response.status));
  return data;
}

// FastAPI sends a string for our own errors and a list for validation errors.
function errorText(data, status) {
  const detail = data && data.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((d) => d.msg.replace(/^Value error, /, "")).join("; ");
  return `Ошибка сервера (${status})`;
}

// Drops empty values, so only the filters that are set reach the URL.
function query(params) {
  const filled = Object.entries(params).filter(([, v]) => v !== "" && v !== null && v !== undefined && v !== false);
  return filled.length ? `?${new URLSearchParams(filled)}` : "";
}

export const api = {
  listTrains: (filters = {}) => request("GET", `/trains/${query(filters)}`),
  searchTrains: (params) => request("GET", `/trains/search/${query(params)}`),
  getTrain: (number) => request("GET", `/trains/${number}/`),
  addTrain: (train) => request("POST", "/trains/", train),
  deleteTrain: (number) => request("DELETE", `/trains/${number}/`),

  listCountries: () => request("GET", "/countries/"),
  addCountry: (country) => request("POST", "/countries/", country),
  renameCountry: (code, name) => request("PATCH", `/countries/${code}/`, { name }),
  deleteCountry: (code) => request("DELETE", `/countries/${code}/`),
  listCities: () => request("GET", "/cities/"),
  addCity: (city) => request("POST", "/cities/", city),
  updateCity: (id, changes) => request("PATCH", `/cities/${id}/`, changes),
  deleteCity: (id) => request("DELETE", `/cities/${id}/`),

  reportByCountry: () => request("GET", "/reports/countries/"),
  reportBusiestCities: () => request("GET", "/reports/cities/"),

  explain: () => request("GET", "/explain/"),
  listIndexes: () => request("GET", "/indexes/"),
  bulkFill: () => request("POST", "/demo/bulk/"),
  resetDemo: () => request("POST", "/demo/reset/"),
};

// A train as the API returns it -> the body POST /trains expects (used by undo).
export function trainToInput(train) {
  return {
    number: train.number,
    destination_id: train.destination.id,
    departure: train.departure,
    stops: train.stops.map((stop) => stop.id),
  };
}
