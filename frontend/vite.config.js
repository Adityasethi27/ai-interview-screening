import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy API + health calls to the FastAPI backend during development,
// so the frontend can use same-origin relative URLs (no CORS friction).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});
