import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      include: ["**/*.tsx", "**/*.ts", "**/*.jsx", "**/*.js"],
    }),
  ],
  server: {
    watch: {
      usePolling: true,
    },
    hmr: true,
    host: true,
    strictPort: true,
  },
});
