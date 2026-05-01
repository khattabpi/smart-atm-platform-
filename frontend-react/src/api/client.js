import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

// Inject JWT on every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-logout on 401
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      if (window.location.pathname !== "/login") window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data) => client.post("/auth/register", data),
  login: (data) => client.post("/auth/login", data),
};

export const profileAPI = {
  getBanks: () => client.get("/profile/banks"),
  getMe: () => client.get("/profile/me"),
  update: (data) => client.put("/profile/me", data),
};

export const atmAPI = {
  getNearby: (params) => client.get("/atms/nearby", { params }),
  getRecommendation: (data) => client.post("/recommendations/", data),
  submitReport: (data) => client.post("/reports/", data),
};

export const txAPI = {
  create: (data) => client.post("/transactions/", data),
  list: () => client.get("/transactions/"),
  analytics: () => client.get("/transactions/analytics"),
};

export default client;