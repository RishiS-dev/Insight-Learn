import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

const THEMES = ["bumblebee", "night"];

export default function ThemeToggle({ className = "" }) {
  const [theme, setTheme] = useState(
    typeof window !== "undefined" ? localStorage.getItem("theme") || THEMES[0] : THEMES[0]
  );

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const isDark = theme === "night";

  return (
    <button
      type="button"
      onClick={() => setTheme(isDark ? "lemonade" : "night")}
      className={`btn btn-ghost btn-square ${className}`}
      aria-label="Toggle theme"
      title="Toggle theme"
    >
      {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
    </button>
  );
}