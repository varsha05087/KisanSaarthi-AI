/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#E8F5E9',
          100: '#C8E6C9',
          500: '#4CAF50',
          600: '#388E3C',
          DEFAULT: '#2E7D32',
          dark: '#1B5E20',
        },
        leaf: {
          light: '#A5D6A7',
          DEFAULT: '#66BB6A',
          dark: '#43A047',
        },
        harvest: {
          light: '#FFF9C4',
          DEFAULT: '#F9A825',
          dark: '#F57F17',
        },
        earth: {
          bg: '#FAF8F2',
          card: '#FFFFFF',
          text: '#26332A',
          muted: '#66736A',
          border: '#E3E0D8',
          subtle: '#F2EFE9',
        },
        info: {
          DEFAULT: '#1976D2',
          light: '#E3F2FD',
        },
        danger: {
          DEFAULT: '#D32F2F',
          light: '#FFEBEE',
        },
      },
      fontFamily: {
        sans: [
          'Noto Sans',
          'Noto Sans Telugu',
          'Noto Sans Devanagari',
          'system-ui',
          '-apple-system',
          'sans-serif',
        ],
        telugu: ['Noto Sans Telugu', 'Gautami', 'Vani', 'sans-serif'],
        hindi: ['Noto Sans Devanagari', 'Mangal', 'sans-serif'],
      },
      boxShadow: {
        'farmer': '0 4px 16px -2px rgba(46, 125, 50, 0.08), 0 2px 6px -1px rgba(38, 51, 42, 0.05)',
        'farmer-lg': '0 10px 25px -3px rgba(46, 125, 50, 0.12), 0 4px 10px -2px rgba(38, 51, 42, 0.06)',
        'pulse-ring': '0 0 0 8px rgba(46, 125, 50, 0.15)',
        'pulse-record': '0 0 0 12px rgba(211, 47, 47, 0.2)',
      },
      animation: {
        'pulse-slow': 'pulse 2.5s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'ripple': 'ripple 1.8s ease-out infinite',
      },
      keyframes: {
        ripple: {
          '0%': { transform: 'scale(0.95)', opacity: '1' },
          '100%': { transform: 'scale(1.35)', opacity: '0' },
        },
      },
    },
  },
  plugins: [],
};
