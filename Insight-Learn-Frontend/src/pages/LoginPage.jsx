import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { Link } from "react-router-dom";
import ThemeToggle from "../components/ui/ThemeToggle";

export default function LoginPage() {
  const { doLogin, loading, error } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function submit(e) {
    e.preventDefault();
    doLogin(email, password);
  }

  return (
    <div className="min-h-screen relative grid place-items-center px-4">
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <form onSubmit={submit} className="card w-full max-w-sm bg-base-100 shadow-md">
        <div className="card-body">
          <h1 className="card-title">Sign in</h1>
          {error && <div className="alert alert-error text-sm">{error}</div>}

          <label className="form-control">
            <span className="label-text">Email</span>
            <input className="input input-bordered" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>

          <label className="form-control">
            <span className="label-text">Password</span>
            <input className="input input-bordered" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>

          <button className={`btn btn-primary w-full ${loading ? "btn-disabled" : ""}`}>
            {loading ? "Signing in..." : "Login"}
          </button>

          <div className="text-xs text-center opacity-70">
            No account? <Link to="/register" className="link link-primary">Register</Link>
          </div>
        </div>
      </form>
    </div>
  );
}