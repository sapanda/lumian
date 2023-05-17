/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],

  theme: {
    borderColor: (theme) => ({
      ...theme("colors"),
    }),
    padding: (theme) => ({
      ...theme("spacing"),
    }),

    fontFamily: {
      sans: ["Poppins", "sans-serif"],
    },
    extend: {
      colors: {
        blue300: "#58A0E2",
        blue500: "#0268C6",
        blue900: "#0E5596",

        gray100: "#FAFAFA",
        gray200: "#E9E9E9",
        gray300: "#D9D9D9",
        gray500: "#707070",
        gray600: "#5B5B5B",
        gray900: "#212121",

        black: "#000000",
        white: "#FFFFFF",
      },
      textColor: {
        blue500: "#0268C6",
        blue900: "#0E5596",

        gray100: "#FAFAFA",
        gray200: "#E9E9E9",
        gray300: "#D9D9D9",
        gray500: "#707070",
        gray600: "#5B5B5B",
        gray900: "#212121",

        black: "#000000",
        white: "#FFFFFF",
      },

      boxShadow: {
        card: "0px 4px 40px rgba(0, 0, 0, 0.2)",
        container: "0px 0px 6px rgba(0, 0, 0, 0.25)",
      },
      maxWidth: {},
      height: {},
      fontSize: {
        "32-600": ["2rem", { lineHeight: "2.5rem", fontWeight: "600" }],
        "24-700": ["1.5rem", { lineHeight: "2rem", fontWeight: "700" }],
        "20-700": ["1.25rem", { lineHeight: "1.75rem", fontWeight: "700" }],
        "16-500": ["1rem", { lineHeight: "1.5rem", fontWeight: "500" }],
        "14-700": ["0.875rem", { lineHeight: "1.25rem", fontWeight: "700" }],
        "14-600": ["0.875rem", { lineHeight: "1.25rem", fontWeight: "600" }],
        "14-500": ["0.875rem", { lineHeight: "1.25rem", fontWeight: "500" }],
        "14-400": ["0.875rem", { lineHeight: "1.25rem", fontWeight: "400" }],
        "12-700": ["0.75rem", { lineHeight: "1rem", fontWeight: "700" }],
        "12-500": ["0.75rem", { lineHeight: "1rem", fontWeight: "500" }],
        "12-400": ["0.75rem", { lineHeight: "1rem", fontWeight: "400" }],
      },
    },
  },

  plugins: [],
};
