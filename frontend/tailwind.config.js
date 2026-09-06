/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#0A0D14',
          900: '#0E1219',
          800: '#131826',
          700: '#1A2032',
          600: '#232A3D',
          500: '#2E374E',
        },
        line: '#212940',
        muted: '#818CA3',
        faint: '#4E586F',
        paper: '#E9ECF3',
        accent: {
          DEFAULT: '#4C7CF3',
          soft: '#4C7CF31A',
          hover: '#6690F5',
        },
        risk: {
          high: '#F1546B',
          highSoft: '#F1546B1A',
          medium: '#F0A83C',
          mediumSoft: '#F0A83C1A',
          low: '#34C77B',
          lowSoft: '#34C77B1A',
        },
      },
      fontFamily: {
        sans: ['Manrope', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
      boxShadow: {
        panel: '0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.5)',
      },
      borderRadius: {
        md2: '10px',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: 0, transform: 'translateY(4px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { transform: 'translateX(16px)', opacity: 0 },
          '100%': { transform: 'translateX(0)', opacity: 1 },
        },
      },
      animation: {
        fadeIn: 'fadeIn 0.25s ease-out',
        slideIn: 'slideIn 0.2s ease-out',
      },
    },
  },
  plugins: [],
}
