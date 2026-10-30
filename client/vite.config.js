import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    fs: { allow: [".."] },
    proxy: {
      "/djangoapp": "http://127.0.0.1:8000",
      "/fetchDealers": "http://127.0.0.1:8000",
      "/fetchDealer": "http://127.0.0.1:8000",
      "/fetchReviews": "http://127.0.0.1:8000",
      "/analyze": "http://127.0.0.1:8000"
    }
  }
});
