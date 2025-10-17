import { useState } from "react";
import { login, registerUser } from "../api/auth";

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  function extractToken(data) {
    // Prefer access_token, but be resilient to other shapes
    return (
      data?.access_token ??
      data?.token ??
      data?.["access token"] ??
      null
    );
  }

  async function doLogin(email, password) {
    setLoading(true); setError(null);
    try {
      const data = await login(email, password);
      const token = extractToken(data);
      if (!token) {
        throw new Error("Token missing in response");
      }
      localStorage.setItem("access_token", token);
      window.location.href = "/";
    } catch (e) {
      const msg =
        e.response?.data?.detail ||
        e.message ||
        "Login failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  async function doRegister(name, email, password) {
    setLoading(true); setError(null);
    try {
      await registerUser(name, email, password);
      await doLogin(email, password);
    } catch (e) {
      const msg =
        e.response?.data?.detail ||
        e.message ||
        "Registration failed";
      setError(msg);
      setLoading(false);
    }
  }

  return { loading, error, doLogin, doRegister };
}