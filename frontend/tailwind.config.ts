import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        coffee: {
          50:  "#fdf8f0",
          100: "#f9ecda",
          200: "#f2d5b0",
          300: "#e8b87e",
          400: "#dc924a",
          500: "#c97328",
          600: "#b85d1f",
          700: "#97461c",
          800: "#7b3a1e",
          900: "#65311c",
        },
      },
      fontFamily: {
        sans:    ["var(--font-sans)",    "system-ui", "sans-serif"],
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        mono:    ["var(--font-mono)",    "Menlo",     "monospace"],
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      animation: {
        "slide-in-left":  "slideInLeft 0.28s ease-out both",
        "fade-in-up":     "fadeInUp 0.35s ease-out both",
        "badge-bounce":   "badgeBounce 0.45s ease-out both",
        "fade-in":        "fadeIn 0.3s ease-out both",
        "role-stripe":    "roleStripe 0.5s ease-out both",
        "stat-pop":       "statPop 0.4s ease-out both",
      },
      keyframes: {
        slideInLeft: {
          from: { opacity: "0", transform: "translateX(-10px)" },
          to:   { opacity: "1", transform: "translateX(0)" },
        },
        fadeInUp: {
          from: { opacity: "0", transform: "translateY(14px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
        badgeBounce: {
          "0%":   { transform: "scale(0.6)", opacity: "0" },
          "60%":  { transform: "scale(1.15)" },
          "80%":  { transform: "scale(0.95)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to:   { opacity: "1" },
        },
        roleStripe: {
          from: { opacity: "0", transform: "scaleX(0.4)" },
          to:   { opacity: "1", transform: "scaleX(1)" },
        },
        statPop: {
          "0%":   { opacity: "0", transform: "translateY(16px) scale(0.97)" },
          "60%":  { transform: "translateY(-2px) scale(1.01)" },
          "100%": { opacity: "1", transform: "translateY(0) scale(1)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
