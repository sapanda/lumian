import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    hmr: process.env.DEPLOY_MODE === "local" ? true : false,
    watch: {
      usePolling: true,
    },
    host: true,
    strictPort: true,
  },
});
