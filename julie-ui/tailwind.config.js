/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'julie-cyan': '#00f0ff',
        'julie-bg': 'rgba(10, 10, 10, 0.85)',
      },
      animation: {
        'waveform': 'waveform 1.2s ease-in-out infinite',
      },
      keyframes: {
        waveform: {
          '0%, 100%': { transform: 'scaleY(0.5)' },
          '50%': { transform: 'scaleY(1.5)' },
        }
      }
    },
  },
  plugins: [],
}
