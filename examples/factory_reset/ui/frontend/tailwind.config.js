/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'nvidia-green': '#76b900',
        'nvidia-dark': '#1a1a1a',
        'chat-bg': '#f8fafc',
        'message-user': '#3b82f6',
        'message-bot': '#e5e7eb',
      },
      animation: {
        'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounce 1s infinite',
      }
    },
  },
  plugins: [],
}
