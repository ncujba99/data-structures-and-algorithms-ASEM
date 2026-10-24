// A query as the backend builds it (Python, SQLAlchemy) and as PostgreSQL receives it (SQL),
// folded away until asked for.
export default function SqlBlock({ query, open = false }) {
  return (
    <details open={open}>
      <summary>Запрос: Python → SQL</summary>
      <div className="query">
        <p className="query-label">Python (SQLAlchemy)</p>
        <pre>{query.python.trim()}</pre>
        <p className="query-label">SQL, который из него собирает SQLAlchemy</p>
        <pre>{query.sql.trim()}</pre>
      </div>
    </details>
  );
}
