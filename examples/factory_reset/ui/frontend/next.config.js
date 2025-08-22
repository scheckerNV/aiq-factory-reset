/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production'
          ? 'http://dcgm-chat-backend:8000/:path*'
          : 'http://localhost:8000/:path*'
      }
    ]
  }
}

module.exports = nextConfig
