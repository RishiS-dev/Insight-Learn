import api from "./client";

export const login = (email, password) =>
  api.post("/auth/login", { email, password }).then(r => r.data);

export const registerUser = (name, email, password) =>
  api.post("/auth/register", { name, email, password }).then(r => r.data);