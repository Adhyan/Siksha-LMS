import type { NextConfig } from 'next';
const config: NextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  async rewrites() {
    return [{
      source: '/api-proxy/:path*',
      destination: 'http://127.0.0.1:8000/:path*',
    }];
  },
};
export default config;
