/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'standalone',
  async rewrites() {
    const backendPort = process.env.BACKEND_PORT || '8080';
    return [
      {
        source: '/api/:path*',
        destination: `http://localhost:${backendPort}/:path*`
      },
      {
        source: '/ws/:path*',
        destination: `http://localhost:${backendPort}/ws/:path*`
      }
    ]
  }
}

module.exports = nextConfig
