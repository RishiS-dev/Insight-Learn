import axios from "axios";

// Use Vite proxy in dev: baseURL = "/api"
// In production, you can still use an absolute URL via env
const baseURL =
  (import.meta.env.PROD && import.meta.env.VITE_API_BASE_URL) || "/api";

// TEMP log to confirm
if (typeof window !== "undefined") {
  console.log("API baseURL =", baseURL);
}

const api = axios.create({ baseURL });

// Also set global default in case someone imports axios directly
axios.defaults.baseURL = baseURL;

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem("access_token");
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  console.log("REQ:", (cfg.baseURL || "") + (cfg.url || ""), cfg.method?.toUpperCase());
  return cfg;
});

api.interceptors.response.use(
  r => r,
  err => {
    const status = err?.response?.status;
    const url = err?.config?.url || "";
    const isAuthRoute = url.includes("/auth/login") || url.includes("/auth/register");
    if (status === 401 && !isAuthRoute) {
      localStorage.removeItem("access_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

export default api;