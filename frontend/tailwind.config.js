/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f4f6f8',
          100: '#e5e9ee',
          500: '#2c3e50',
          600: '#1a252f',
          accent: '#e67e22',
        }
      }
    },
  },
  plugins: [],
}