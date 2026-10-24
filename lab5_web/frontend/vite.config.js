import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Inside docker compose the backend is reachable by its service name.
const backend = process.env.BACKEND_URL || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // The browser only talks to this server; /api is forwarded to FastAPI, so no CORS is needed.
    proxy: { "/api": backend },
  },
});
