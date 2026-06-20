module.exports = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#101828',
        mist: '#f8fafc',
        veil: '#e4ebf4',
        accent: '#2563eb',
        accentSoft: '#dbeafe'
      },
      boxShadow: {
        glow: '0 20px 60px rgba(37, 99, 235, 0.14)'
      },
      backgroundImage: {
        'dashboard-grid': 'radial-gradient(circle at top left, rgba(37,99,235,.10), transparent 30%), linear-gradient(180deg, #f8fafc 0%, #eef4ff 100%)'
      }
    }
  },
  plugins: [require('@tailwindcss/typography')]
};
