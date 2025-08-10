/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        black: {
          DEFAULT: '#060505',
          100: '#010101',
          200: '#020202',
          300: '#030303',
          400: '#040404',
          500: '#060505',
          600: '#3c3232',
          700: '#736060',
          800: '#a49292',
          900: '#d2c9c9'
        },
        white: {
          DEFAULT: '#ffffff',
          100: '#333333',
          200: '#666666',
          300: '#999999',
          400: '#cccccc',
          500: '#ffffff',
          600: '#ffffff',
          700: '#ffffff',
          800: '#ffffff',
          900: '#ffffff'
        },
        rojo: {
          DEFAULT: '#d82423',
          100: '#2b0707',
          200: '#560e0e',
          300: '#811515',
          400: '#ac1c1c',
          500: '#d82423',
          600: '#e24c4c',
          700: '#e97979',
          800: '#f0a6a6',
          900: '#f8d2d2'
        },
        azure: {
          DEFAULT: '#d3e4e9',
          100: '#1e343b',
          200: '#3b6876',
          300: '#5d9bad',
          400: '#98bfcb',
          500: '#d3e4e9',
          600: '#dce9ed',
          700: '#e5eff2',
          800: '#edf4f6',
          900: '#f6fafb'
        },
        vista: {
          DEFAULT: '#7f9ec3',
          100: '#151f2c',
          200: '#293e57',
          300: '#3e5d83',
          400: '#537cae',
          500: '#7f9ec3',
          600: '#98b1cf',
          700: '#b2c4db',
          800: '#ccd8e7',
          900: '#e5ebf3'
        }
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
        'bounce-slow': 'bounce 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-custom': 'linear-gradient(135deg, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [],
};
