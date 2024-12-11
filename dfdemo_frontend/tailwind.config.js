/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          default: '#f97316',
        },
        borderOrange: '#BE7123',
        black: '#121212',
        dark: '#2B2B2B',
        txtgreen: '#8AE288',
        txtgray: '#D1D1D1',
        btngreen: '#79C077'
      },
      backgroundImage: {
        // 'gradient-red-orange': 'linear-gradient(213deg, rgba(255,77,39,0.7) 0%, rgba(78,27,27,1) 100%)',
        'gradient-red-orange': 'linear-gradient(213deg, rgba(255,100,0,0.8) 0%, rgba(255,30,0,0.7) 100%)',
        'gradient-yellow': 'linear-gradient( 135deg, #F7EA76 0%, #D1AF4D 100%)',
        'gradient-bg': 'linear-gradient( 190deg, #349F31 0%, #FA7107 100%);',
        'bg-global': "url('/images/bg_global.png')"
      },
      boxShadow: {
        'custom-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
      },
      margin: {
        '72': '18rem', // 72 * 4px = 288px
        '80': '20rem', // 80 * 4px = 320px
        '96': '24rem', // 96 * 4px = 384px
        '128': '32rem', // 128 * 4px = 512px
        '144': '36rem', // 144 * 4px = 576px
        '160': '40rem', // 160 * 4px = 640px
        '192': '48rem', // 192 * 4px = 768px
      }
    },
  },
  plugins: [],
}
