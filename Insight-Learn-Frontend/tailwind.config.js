/** @type {import('tailwindcss').Config} */
import daisyui from "daisyui";

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}"
  ],
  theme: {
    extend: {
      boxShadow: {
        sm: "0 1px 2px rgba(0,0,0,0.08)",
        md: "0 3px 10px rgba(0,0,0,0.10)"
      },
      borderRadius: { sm: "4px", md: "8px", lg: "14px" },
      spacing: { "1.5": "0.375rem" },
      transitionDuration: { fast: "150ms" }
    }
  },
  plugins: [daisyui],
  daisyui: {
    themes: ["lemonade", "night"],
    darkTheme: "night"
  }
}