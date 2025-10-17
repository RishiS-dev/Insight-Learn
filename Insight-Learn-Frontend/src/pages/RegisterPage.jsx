import { useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { Link } from "react-router-dom";
import ThemeToggle from "../components/ui/ThemeToggle";

export default function RegisterPage() {
  const { doRegister, loading, error } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [localError, setLocalError] = useState("");

  function submit(e) {
    e.preventDefault();
    setLocalError("");

    if (password !== confirm) {
      setLocalError("Passwords do not match.");
      return;
    }
    if (password.length < 6) {
      setLocalError("Password must be at least 6 characters.");
      return;
    }

    doRegister(name.trim(), email.trim(), password);
  }

  return (
    <div className="min-h-screen relative grid place-items-center px-4">
      {/* Theme toggle at top-right */}
      <div className="absolute top-4 right-4">
        <ThemeToggle />
      </div>

      <form onSubmit={submit} className="card w-full max-w-sm bg-base-100 shadow-md">
        <div className="card-body gap-4">
          <div className="flex items-center justify-between">
            <h1 className="card-title">Create account</h1>
            <span className="text-xs opacity-60">It’s quick and easy</span>
          </div>

          {(localError || error) && (
            <div className="alert alert-error py-2 text-sm">
              <span>{localError || error}</span>
            </div>
          )}

          <label className="form-control">
            <span className="label-text">Full name</span>
            <input
              className="input input-bordered"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Jane Doe"
              required
            />
          </label>

          <label className="form-control">
            <span className="label-text">Email</span>
            <input
              className="input input-bordered"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="jane@example.com"
              required
            />
          </label>

          <div className="grid grid-cols-1 gap-4">
            <label className="form-control">
              <div className="label">
                <span className="label-text">Password</span>
                <span className="label-text-alt opacity-60">Min 6 chars</span>
              </div>
              <input
                className="input input-bordered"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </label>

            <label className="form-control">
              <span className="label-text">Confirm password</span>
              <input
                className="input input-bordered"
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                placeholder="••••••••"
                required
              />
            </label>
          </div>

          <button
            className={`btn btn-primary w-full ${loading ? "btn-disabled" : ""}`}
            disabled={loading}
            type="submit"
          >
            {loading ? "Creating..." : "Register"}
          </button>

          <div className="text-xs text-center opacity-70">
            Already have an account?{" "}
            <Link to="/login" className="link link-primary">
              Sign in
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}