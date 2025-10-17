import { Link } from "react-router-dom";
import ThemeToggle from "../ui/ThemeToggle";

export default function TopBar() {
  return (
    <div className="navbar bg-base-100 border-b">
      <div className="flex-1">
        {/* Make brand clickable to go to dashboard */}
        <Link
          to="/"
          className="btn btn-ghost normal-case text-lg font-semibold px-2"
          title="Go to Dashboard"
          aria-label="Go to Dashboard"
        >
          InsightLearn
        </Link>
      </div>
      <div className="flex-none gap-2">
        <ThemeToggle />
        <button
          className="btn btn-ghost text-sm"
          onClick={() => {
            localStorage.removeItem("access_token");
            window.location.href = "/login";
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
}