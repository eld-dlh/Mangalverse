/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        mars: {
          darkest: '#090a0f',
          darker: '#11141e',
          dark: '#181d2c',
          panel: '#1f2538',
          border: '#2c354e',
          rust: '#c1440e',
          red: '#e24e1b',
          orange: '#ff6b35',
          gold: '#e9b872',
          cyan: '#00d2ff',
          neon: '#00ffc8'
        }
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace'],
      }
    },
  },
  plugins: [],
}
