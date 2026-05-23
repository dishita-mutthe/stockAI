import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy /api → FastAPI dev server so the React app can call the backend
// without CORS gymnastics during development.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
