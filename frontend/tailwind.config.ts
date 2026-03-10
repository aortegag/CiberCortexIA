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
      // ---------------------------------------------------------------
      // CiberCortex IA Design System v1.0.0
      // All color tokens are CANONICAL — do not override
      // ---------------------------------------------------------------
      colors: {
        // Dark backgrounds
        canvas:  "#080C15",   // outermost shell
        surface: "#0F1623",   // cards, panels
        raised:  "#1A2233",   // raised elements, hover states

        // Severity palette — IMMUTABLE (1 color = 1 meaning)
        critical: "#FF4545",
        high:     "#FF8C00",
        medium:   "#F0B429",
        low:      "#4B8BFF",
        pass:     "#22C55E",
        info:     "#6B7280",

        // Border
        border: "#1E2D42",

        // Text hierarchy
        "text-primary":   "#F1F5F9",
        "text-secondary": "#94A3B8",
        "text-muted":     "#475569",

        // Brand accent
        brand: "#3B82F6",
        "brand-hover": "#2563EB",
      },
      fontFamily: {
        sans:  ["var(--font-geist-sans)", "Inter", "system-ui", "sans-serif"],
        mono:  ["var(--font-geist-mono)", "JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        "2xs": ["0.65rem", { lineHeight: "1rem" }],
      },
      height: {
        "row": "44px",   // canonical table row height
      },
      width: {
        "sidebar": "220px",
      },
      borderRadius: {
        DEFAULT: "0.375rem",
        lg: "0.5rem",
        xl: "0.75rem",
      },
      boxShadow: {
        "surface": "0 0 0 1px #1E2D42",
        "raised":  "0 4px 24px rgba(0,0,0,0.4)",
      },
      keyframes: {
        "shimmer": {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(4px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.5s infinite linear",
        "fade-in": "fade-in 0.2s ease-out",
      },
    },
  },
  plugins: [],
};

export default config;
