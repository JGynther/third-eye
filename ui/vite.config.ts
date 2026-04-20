import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  server: {
    host: true,
    allowedHosts: ["nixos-gaming"],
    proxy: {
      "/api": {
        target: "http://localhost:8001",
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
